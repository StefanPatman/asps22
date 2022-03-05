
from yaml import safe_load
from sys import argv
import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic


def create_generator_node(name=None) -> Node:

    id = next(counters["generator"])
    name = name if name is not None else f'generator_{id}'

    node = create_node(name=name,
                       cpus=1, arch='arm32', mem='512M',
                       labels={
                           'ether.edgerun.io/type': 'server',
                           'ether.edgerun.io/model': 'server'
                       })
    node.service = 'generator'
    node.id = id
    node.aggregator_node = ...
    return node


def create_aggregator_node(name=None) -> Node:

    name = name if name is not None else f'aggregator_{next(counters["aggregator"])}'

    return create_node(name=name,
                       cpus=4, arch='x86', mem='2G',
                       labels={
                           'ether.edgerun.io/type': 'server',
                           'ether.edgerun.io/model': 'server'
                       })


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
        self.processor = f'processor_{next(counters["processor"])}'

    def _create_processor_node(self) -> Node:
        return create_node(
            name=self.processor,
            cpus=8, arch='x86', mem='16G',
            labels={
            'ether.edgerun.io/type': 'server',
            'ether.edgerun.io/model': 'server'
        })

    def _create_rack_gen(self, generators):
        def _create_rack():
            return LANCell([create_generator_node] * generators + [create_aggregator_node], backhaul=self.switch)
        return _create_rack


    # def materialize(self, topology: Topology, parent=None):
    #     self._create_identity()
    #
    #     for cell in self.nodes:
    #         self._materialize(topology, cell, self.switch)
    #
    #     if self.backhaul:
    #         if isinstance(self.backhaul, UpDownLink):
    #             uplink = Link(self.backhaul.bw_up, tags={'type': 'uplink', 'name': 'up_%s' % self.name})
    #             downlink = Link(self.backhaul.bw_down, tags={'type': 'downlink', 'name': 'down_%s' % self.name})
    #
    #             topology.add_connection(Connection(self.switch, uplink, latency_dist=self.backhaul.latency_dist),
    #                                     directed=True)
    #             topology.add_connection(Connection(downlink, self.switch), directed=True)
    #
    #             topology.add_connection(Connection(self.backhaul.backhaul, downlink,
    #                                                latency_dist=self.backhaul.latency_dist), directed=True)
    #             topology.add_connection(Connection(uplink, self.backhaul.backhaul), directed=True)
    #
    #         else:
    #             topology.add_connection(Connection(self.switch, self.backhaul, latency_dist=latency.lan))


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


def main(input):
    topology = Topology()

    for city, factories in input.items():
        City(factories, internet='internet').materialize(topology)

    # CustomIoTScenario(num_premises=2, internet='internet_chix').materialize(topology)
    # CustomIoTScenario(num_premises=2, internet='internet_nyc').materialize(topology)

    # topology.add_connection(Connection('internet_chix', 'internet_nyc', 10))

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()  # display

    # for n in topology.get_nodes():
    #     for j in topology.get_nodes():
    #         if type(n) == Node and type(j) == Node and n != j:
    #              bandwidth = min([k.bandwidth for k in topology.route(n, j).hops])
    #              latency = round(float(topology.route(n, j).rtt/2), 2)
    #              print(n,j,bandwidth,latency)

    return topology



if __name__ == '__main__':
    file = argv[1]
    with open(file) as stream:
        input = safe_load(stream)
    main(input)
