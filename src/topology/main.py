
from yaml import safe_load, dump
from sys import argv
import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

from config import create_config
from scenario import create_topology


def main(input):
    topology = create_topology(input)

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()  # display

    config = create_config(topology)
    print(dump(config))

    return topology


if __name__ == '__main__':
    file = argv[1]
    with open(file) as stream:
        input = safe_load(stream)
    main(input)
