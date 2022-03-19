
from yaml import safe_load, dump
from sys import argv
from itertools import chain
import matplotlib.pyplot as plt

from srds import ParameterizedDistribution as PDist
from collections import defaultdict, Iterable
from typing import Callable, List, Union

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink, Host
from ether.topology import Topology
from ether.vis import draw_basic
from ether.qos import latency

from config import create_config
from extensions import create_node_multicore


CONFIG = {
    'generator': {
        'cores': 1,
        'clock': 100,
        'mem': '128Mi',
    },
    'aggregator': {
        'cores': 1,
        'clock': 100,
        'mem': '256Mi',
    },
    'processor': {
        'cores': 2,
        'clock': 100,
        'mem': '256Mi',
    },
    'app': {
        'interval': 1,
        'history': 10,
        'window': 10,
        'busy_wait': 0,
    },
}

class Floor(LANCell):

    def __init__(self, label, factory, aggregators, latency, factory_latency, backhaul=None, config=CONFIG) -> None:
        self.label=label
        self.config = config
        self.factory = factory
        self.aggregators = aggregators
        self.factory_latency = factory_latency
        self.latency = PDist.lognorm((latency['sigma'], latency['loc'], latency['scale']))
        nodes = [self._create_aggregator_group(a, g) for a, g in aggregators.items()]
        super().__init__(chain(nodes), backhaul=backhaul)

    def _create_identity(self):
        self.nr = next(counters['floor'])
        self.name = f'floor_{self.nr}'
        self.switch = f'switch_{self.name}'

    def _materialize(self, topology: Topology, c: object, backhaul=None):
        if isinstance(c, Iterable):
            for elem in c:
                self._materialize(topology, elem, backhaul)
            return

        if callable(c):
            c = c()

        if isinstance(c, Node):
            c = Host(c, backhaul=backhaul)
            c.materialize(topology, self, latency_dist=self.latency)
            return
        elif isinstance(c, Cell):
            if backhaul:
                c.backhaul = backhaul

        c.materialize(topology, self)

    def materialize(self, topology: Topology, parent=None):
        self._create_identity()

        for cell in self.nodes:
            self._materialize(topology, cell, self.switch)

        if self.backhaul:
            topology.add_connection(Connection(self.switch, self.backhaul, latency_dist=self.factory_latency))

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
                    'asps.window': self.config['app']['window'],
                    'asps.busy_wait': self.config['app']['busy_wait'],
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
                    'asps.interval': self.config['app']['interval'],
                    'asps.service': 'generator',
                    'asps.aggregator': aggregator_name,
                    'asps.id': id,
                })
            return node

        return [_create_aggregator_node] + [_create_generator_node] * generator_count


class Factory(LANCell):

    def __init__(self, label, floors, latency, host_port=None, backhaul=None, config=CONFIG) -> None:
        self.label=label
        self.config=config
        self.latency = PDist.lognorm((latency['sigma'], latency['loc'], latency['scale']))
        self.host_port=host_port
        cloudlet_nodes = [
            self._create_floor_gen(floor, desc)
            for floor, desc in floors.items()
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
            'asps.host_port': self.host_port,
            'asps.history': self.config['app']['history'],
            'asps.service': 'processor',
            'asps.id': self.processor_id,
        })

    def _create_floor_gen(self, floor, desc):
        aggregators = desc['aggregators']
        latency = desc['latency']
        def _create_floor():
            return Floor(floor, self, aggregators, latency, factory_latency=self.latency, backhaul=self.switch, config=self.config)
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

        for factory, desc in self.factories.items():
            floors = desc['floors']
            latency = desc['latency']
            host_port = desc.get('host_port', 0)
            cloudlet = Factory(factory, floors, latency, host_port=host_port, backhaul=UpDownLink(10000, 10000, backhaul=city.switch), config=self.config)
            cloudlet.materialize(topology)

def create_topology(input, config):
    topology = Topology()
    for city, factories in input.items():
        City(factories, internet='internet', config=config).materialize(topology)
    return topology
