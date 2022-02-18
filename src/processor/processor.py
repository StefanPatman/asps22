from flask import Flask, request, jsonify
import logging
from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1

class Aggregator:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.route = 'listen'

    def url(self):
        return f'http://{self.ip}:{self.port}/{self.route}'

class Processor:
    def __init__(self):
        self.t = 100
        self.elements = {}
    def listen(self, id, data):
        if self.elements.get(id) is None:
            self.elements[id] = []
        self.elements[id].append(data)
        if len(self.elements[id]) >= self.t :
            d = self.condense(id)
            self.post(d)
    def condense(self, id):
        s = 0
        s = sum(x['temperature'] for x in self.elements[id])
        l = len(self.elements[id])
        median = s/l
        last = self.elements[id][-1]
        data = {
            'location' : last['location'],
            'timestamp' : last['timestamp'],
            'temperature' : median,
            'id' : id,
        }
        self.elements[id] = []
        return data
    def post(self, data):
        print(data)
        post(self.aggregator.url(), json=data)



p = Processor()


app = Flask(__name__)

@app.route('/listen', methods = ['POST'])
def listen():
    logging.info('Enter')
    data = request.get_json()
    temperature = data['temperature']
    location = data['location']
    timestamp = data['timestamp']
    id = int(data['id'])
    print(temperature, location, id, timestamp)
    p.listen(id, data)
    print(p.elements)

    return {}

def main(aggregator, a_port, t, port):
    p.aggregator = Aggregator(aggregator, a_port)
    p.t = t
    app.run(port=port, debug=True)


if __name__ == '__main__':

    q = ArgumentParser(description='ASPS Processor')
    q.add_argument(
        '-a',
        '--aggregator',
        metavar = 'IP:PORT',
        type = str,
        default = '127.0.0.1:5001',
        help = 'Aggregator to post data'
    )
    q.add_argument(
        '-t',
        '--t',
        type = int,
        default = 100,
        help = 'Aggregation period'
    )
    q.add_argument(
        '-p',
        '--port',
        type = int,
        default = 5000,
        help = 'Processor listen port'
    )
    kwargs = vars(q.parse_args())
    kwargs['aggregator'], kwargs['a_port'] = kwargs['aggregator'].split(':')
    main(**kwargs)
