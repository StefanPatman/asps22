
from yaml import safe_load, dump
from sys import argv
from itertools import chain
import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

from config import create_config
from extensions import create_node_multicore


CONFIG = {
    'generator': {
        'cores': 1,
        'clock': 200,
        'mem': '512Mi',
    },
    'aggregator': {
        'cores': 1,
        'clock': 200,
        'mem': '512Mi',
    },
    'processor': {
        'cores': 2,
        'clock': 200,
        'mem': '512Mi',
    },
}

class Floor(LANCell):

    def __init__(self, label, factory, aggregators, backhaul=None, config=CONFIG) -> None:
        self.label=label
        self.config = config
        self.factory = factory
        self.aggregators = aggregators
        nodes = [self._create_aggregator_group(a, g) for a, g in aggregators.items()]
        super().__init__(chain(nodes), backhaul=backhaul)

    def _create_identity(self):
        self.nr = next(counters['floor'])
        self.name = f'floor_{self.nr}'
        self.switch = f'switch_{self.name}'

    def _create_aggregator_group(self, aggregator_name, generator_count):

        aggregator_id = next(counters["aggregator"])
        aggregator_name = f'aggregator_{aggregator_id}'  # ?

        def _create_aggregator_node() -> Node:
            return create_node_multicore(
                name=aggregator_name,
                cores=self.config['aggregator']['cores'],
                clock_speed=self.config['aggregator']['clock'],
                mem=self.config['aggregator']['mem'],
                arch='x86',
                labels={
                    'ether.edgerun.io/type': 'server',
                    'ether.edgerun.io/model': 'server',
                    'asps.service': 'aggregator',
                    'asps.processor': self.factory.processor_name,
                    'asps.id': aggregator_id,
            })

        def _create_generator_node() -> Node:
            id = next(counters["generator"])
            name = f'generator_{id}'

            node = create_node_multicore(
                name=name,
                cores=self.config['generator']['cores'],
                clock_speed=self.config['generator']['clock'],
                mem=self.config['generator']['mem'],
                arch='x86',
                labels={
                    'ether.edgerun.io/type': 'server',
                    'ether.edgerun.io/model': 'server',
                    'asps.floor': self.label,
                    'asps.service': 'generator',
                    'asps.aggregator': aggregator_name,
                    'asps.id': id,
                })
            return node

        return [_create_aggregator_node] + [_create_generator_node] * generator_count


class Factory(LANCell):

    def __init__(self, label, floors, backhaul=None, config=CONFIG) -> None:
        self.label=label
        self.config=config
        cloudlet_nodes = [
            self._create_floor_gen(floor, aggregators)
            for floor, aggregators in floors.items()
        ]
        super().__init__([self._create_processor_node] + cloudlet_nodes, backhaul=backhaul)

    def _create_identity(self):
        self.nr = next(counters['factory'])
        self.name = f'factory_{self.nr}'
        self.switch = f'switch_{self.name}'
        self.processor_id = next(counters["processor"])
        self.processor_name = f'processor_{self.processor_id}'

    def _create_processor_node(self) -> Node:
        return create_node_multicore(
            name=self.processor_name,
            cores=self.config['processor']['cores'],
            clock_speed=self.config['processor']['clock'],
            mem=self.config['processor']['mem'],
            arch='x86',
            labels={
            'ether.edgerun.io/type': 'server',
            'ether.edgerun.io/model': 'server',
            'asps.service': 'processor',
            'asps.id': self.processor_id,
        })

    def _create_floor_gen(self, floor, aggregators):
        def _create_floor():
            return Floor(floor, self, aggregators, backhaul=self.switch, config=self.config)
        return _create_floor


class City:
    """Contains all factories for one city"""
    def __init__(self, factories, internet='internet', config=CONFIG) -> None:
        self.config = config
        super().__init__()
        self.factories = factories
        self.internet = internet

    def materialize(self, topology: Topology):

        city = LANCell([], backhaul=BusinessIsp(self.internet))
        city.materialize(topology)

        for factory, floors in self.factories.items():

            cloudlet = Factory(factory, floors, backhaul=UpDownLink(10000, 10000, backhaul=city.switch), config=self.config)
            cloudlet.materialize(topology)

def create_topology(input, config):
    topology = Topology()
    for city, factories in input.items():
        City(factories, internet='internet', config=config).materialize(topology)
    return topology
