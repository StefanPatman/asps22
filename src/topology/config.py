
from ether.core import Connection, Node, Capacity
from ether.blocks import nodes
from ether.blocks.nodes import create_node
from ether.blocks.cells import IoTComputeBox, Cloudlet, BusinessIsp, counters
from ether.cell import LANCell, SharedLinkCell, UpDownLink
from ether.topology import Topology
from ether.vis import draw_basic

from extensions import CapacityMulticore


# The service description, which is specific to our application,
# should not be part of this file, but provided from main


def _name_node(name):
    return f'{name}_node'


def _name_service(name):
    return f'{name}_service'


def _name_item(name):
    return f'{name}_item'


def create_service_generator(node):
    id = node.labels['asps.id']
    aggregator = node.labels['asps.aggregator']
    return {
        'image': 'generator',
        'environment': [
            'INTERVAL=1',
            f'AGGREGATOR={aggregator}',
            'PORT=5002',
            'LOCATION=Athens',
            f'ID={id}',
        ]
    }


def create_service_aggregator(node):
    id = node.labels['asps.id']
    processor = node.labels['asps.processor']
    return {
        'image': 'aggregator',
        'environment': [
            f'PROCESSOR={processor}',
            'PROCESSOR_PORT=5003',
            f'ID={id}',
        ],
        'ports': [
            '5000:5002'
        ]
    }


def create_service_processor(node):
    id = node.labels['asps.id']
    return {
        'image': 'processor',
        'environment': [
            'PORT=5003',
            f'ID={id}',
        ],
        'ports': [
            '5001:5003'
        ]
    }


def create_service(node):
    service_name = node.labels['asps.service']
    return {
        'generator': create_service_generator,
        'aggregator': create_service_aggregator,
        'processor': create_service_processor,
    }[service_name](node)


def create_services(topology):
    return {
        _name_service(n.name): create_service(n)
        for n in topology.get_nodes()
        if type(n) == Node
    }


def create_networks(topology):
    return {}


def _node_cores(n):
    if isinstance(n.capacity, CapacityMulticore):
        return n.capacity.cores
    return 1


def _node_clock_speed(n):
    if isinstance(n.capacity, CapacityMulticore):
        return n.capacity.clock_speed
    return n.capacity.cpu_millis


def create_node(n):
    return {
        'name': _name_node(n.name),
        'capabilities': {
            'memory': n.capacity.memory,
            'processor': {
                'clock_speed': _node_clock_speed(n),
                'cores': _node_cores(n),
            }
        }
    }

def create_nodes(topology):
    return [create_node(n) for n in topology.get_nodes()]


def create_topology_item(n):
    return {
        'label': _name_item(n.name),
        'node': _name_node(n.name),
        'service': _name_service(n.name),
        'networks': ['internet'],
        'replicas': 1,
    }


def create_topology(topology):
    return [create_topology_item(n) for n in topology.get_nodes()]


def create_config(topology):
    return {
        'version': '3.7',
        'services': create_services(topology),
        'x-fogify': {
            'networks': create_networks(topology),
            'nodes': create_nodes(topology),
            'topology': create_topology(topology),
        }
    }
