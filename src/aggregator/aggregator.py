
from flask import Flask, request, jsonify
import logging
from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1
from os import getenv
from socket import gethostbyname



class Processor:
    def __init__(self, host, port):
        self.ip = gethostbyname(host)
        self.port = port
        self.route = 'listen'

    def url(self):
        return f'http://{self.ip}:{self.port}/{self.route}'

class Aggregator:
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
            'timestamp_last_generated' : last['timestamp_generated'],
            'timestamp_last_aggregated' : last['timestamp_aggregated'],
            'timestamp_computed': time(),
            'temperature' : median,
            'id' : id,
        }
        self.elements[id] = []
        return data
    def post(self, data):
        print(data)
        post(self.processor.url(), json=data)



p = Aggregator()


app = Flask(__name__)

@app.route('/listen', methods = ['POST'])
def listen():
    logging.info('Enter')
    data = request.get_json()
    data['timestamp_aggregated'] = time()
    id = int(data['id'])
    print(data)
    p.listen(id, data)
    # print(p.elements)

    return {}

def main(processor, a_port, t, port):
    p.processor = Processor(processor, a_port)
    p.t = t
    app.run(port=port, host='aggregator', debug=True)


if __name__ == '__main__':
    kwargs = dict(
            port = int(getenv('PORT', 5000)),
            a_port = int(getenv('PROCESSOR_PORT', 5001)),
            processor = getenv('PROCESSOR', 'localhost'),
            t = getenv('T', 10),
    )
    main(**kwargs)
