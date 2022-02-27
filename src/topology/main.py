from srds import ConstantSampler

import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

default_num_cells = 1
default_cell_density = ConstantSampler(10)


def create_generator_node(name=None) -> Node:

    name = name if name is not None else f'generator_{next(counters["generator"])}'

    return create_node(name=name,
                       cpus=88, arch='x86', mem='188G',
                       labels={
                           'ether.edgerun.io/type': 'server',
                           'ether.edgerun.io/model': 'server'
                       })


def create_aggregator_node(name=None) -> Node:

    name = name if name is not None else f'aggregator_{next(counters["aggregator"])}'

    return create_node(name=name,
                       cpus=88, arch='x86', mem='188G',
                       labels={
                           'ether.edgerun.io/type': 'server',
                           'ether.edgerun.io/model': 'server'
                       })



def create_processor_node(name=None) -> Node:

    name = name if name is not None else f'processor_{next(counters["processor"])}'

    return create_node(name=name,
                       cpus=88, arch='x86', mem='188G',
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
        super().__init__(cloudlet_nodes, backhaul=backhaul)

    def _create_identity(self):
        self.nr = next(counters['factory'])
        self.name = f'factory_{self.nr}'
        self.switch = f'switch_{self.name}'

    def _create_rack_gen(self, generators):
        def _create_rack():
            return LANCell([create_generator_node] * generators + [create_aggregator_node], backhaul=self.switch)
        return _create_rack


class CustomIoTScenario:
    def __init__(self, num_premises=default_num_cells, premises_density=default_cell_density,
                 internet='internet') -> None:
        """
        The IIoT scenarios with several factories, that have a factory floor with IoT devices and a on-premises managed
        cloudlet.

        :param num_premises: the number of premises, each premises is a factory with a floor and a cloudlet
        :param premises_density: currently not used, but the idea is that the total number of devices on a premises vary
        according to the parameter. but it's unclear how the total number of devices should be split among the floor and
        the cloudlet.
        :param internet:
        """
        super().__init__()
        self.num_premises = num_premises
        self.premises_density = premises_density
        self.internet = internet

    def materialize(self, topology: Topology):
        for _ in range(self.num_premises):
            floor_compute = IoTComputeBox(nodes=[create_processor_node])

            factory = LANCell([floor_compute], backhaul=BusinessIsp(self.internet))
            factory.materialize(topology)

            cloudlet = Factory({1:1, 2:2, 3:3}, backhaul=UpDownLink(10000, 10000, backhaul=factory.switch))
            cloudlet.materialize(topology)


def main():
    topology = Topology()

    CustomIoTScenario(num_premises=2, internet='internet_chix').materialize(topology)
    CustomIoTScenario(num_premises=2, internet='internet_nyc').materialize(topology)

    topology.add_connection(Connection('internet_chix', 'internet_nyc', 10))

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()  # display


if __name__ == '__main__':
    main()
