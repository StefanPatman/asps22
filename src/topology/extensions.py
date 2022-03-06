
from typing import Dict

from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic
from ether.util import parse_size_string


class CapacityMulticore(Capacity):
    def __init__(self, cores: int = 1, clock_speed: int = 1000, memory: int = 1024 * 1024 * 1024):
        self.memory = memory
        self.cores = cores
        self.clock_speed = clock_speed
        self.cpu_millis = cores * clock_speed

    def __str__(self):
        return f'CapacityMulticore(Cores: {self.cores} Speed {self.clock_speed} Memory: {self.clock_speed})'


def create_node_multicore(name: str, cores: int, clock_speed: int, mem: str, arch: str, labels: Dict[str, str]) -> Node:
    capacity = CapacityMulticore(cores, clock_speed, memory=parse_size_string(mem))
    return Node(name, capacity=capacity, arch=arch, labels=labels)
