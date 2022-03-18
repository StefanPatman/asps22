
from yaml import safe_load, dump
from sys import argv, stdout
import matplotlib.pyplot as plt

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

from scenario import create_topology
from config import create_config


def main(input, visual=True, file=stdout):
    scenario = input['scenario']
    config = input['global']

    topology = create_topology(scenario, config)

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)

    if visual:
        plt.show()

    config = create_config(topology)
    dump(config, file)

    return topology


if __name__ == '__main__':
    file = argv[1]
    with open(file) as stream:
        input = safe_load(stream)
    main(input)
