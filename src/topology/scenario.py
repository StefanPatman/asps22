
from yaml import safe_load, dump
from sys import argv
import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

from config import create_config
from extensions import create_node_multicore


class Floor(LANCell):

    def __init__(self, factory, generator_count, backhaul=None) -> None:
        self.factory = factory
        self.generator_count = generator_count
        generator_nodes = [self._create_generator_node] * generator_count
        super().__init__([self._create_aggregator_node] + generator_nodes, backhaul=backhaul)

    def _create_identity(self):
        self.nr = next(counters['floor'])
        self.name = f'floor_{self.nr}'
        self.switch = f'switch_{self.name}'
        self.aggregator_id = next(counters["aggregator"])
        self.aggregator_name = f'aggregator_{self.aggregator_id}'

    def _create_aggregator_node(self) -> Node:

        return create_node_multicore(
            name=self.aggregator_name,
            cores=2, clock_speed=700,
            arch='x86', mem='2Gi',
            labels={
                'ether.edgerun.io/type': 'server',
                'ether.edgerun.io/model': 'server',
                'asps.service': 'aggregator',
                'asps.processor': self.factory.processor_name,
                'asps.id': self.aggregator_id,
        })

    def _create_generator_node(self) -> Node:

        id = next(counters["generator"])
        name = f'generator_{id}'

        node = create_node_multicore(
            name=name,
            cores=1, clock_speed=300,
            arch='arm32', mem='512Mi',
            labels={
                'ether.edgerun.io/type': 'server',
                'ether.edgerun.io/model': 'server',
                'asps.service': 'generator',
                'asps.aggregator': self.aggregator_name,
                'asps.id': id,
            })
        return node


class Factory(LANCell):

    def __init__(self, generators_per_floor, backhaul=None) -> None:
        cloudlet_nodes = [
            self._create_rack_gen(generators)
            for floor, generators in generators_per_floor.items()
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
            cores=8, clock_speed=1400,
            arch='x86', mem='16Gi',
            labels={
            'ether.edgerun.io/type': 'server',
            'ether.edgerun.io/model': 'server',
            'asps.service': 'processor',
            'asps.id': self.processor_id,
        })

    def _create_rack_gen(self, generators):
        def _create_rack():
            return Floor(self, generators, backhaul=self.switch)
        return _create_rack


class City:
    """Contains all factories for one city"""
    def __init__(self, factories, internet='internet') -> None:

        super().__init__()
        self.factories = factories
        self.internet = internet

    def materialize(self, topology: Topology):

        city = LANCell([], backhaul=BusinessIsp(self.internet))
        city.materialize(topology)

        for factory, floors in self.factories.items():

            cloudlet = Factory(floors, backhaul=UpDownLink(10000, 10000, backhaul=city.switch))
            cloudlet.materialize(topology)

def create_topology(input):
    topology = Topology()
    for city, factories in input.items():
        City(factories, internet='internet').materialize(topology)
    return topology
