
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
        self.window = 10
        self.busy_wait = 0
        self.elements = {}
    def listen(self, id, data):
        if self.elements.get(id) is None:
            self.elements[id] = []
        self.elements[id].append(data)
        if len(self.elements[id]) >= self.window :
            d = self.condense(id)
            self.post(d)
    def condense(self, id):
        s = 0
        s = sum(x['temperature'] for x in self.elements[id])
        l = len(self.elements[id])
        median = s/l
        last = self.elements[id][-1]
        for _ in range(self.busy_wait):
            pass
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

def main(processor, a_port, window, port, busy_wait):
    p.processor = Processor(processor, a_port)
    p.window = window
    p.busy_wait = busy_wait
    app.run(port=port, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    kwargs = dict(
        port = int(getenv('PORT', 5000)),
        a_port = int(getenv('PROCESSOR_PORT', 5001)),
        processor = getenv('PROCESSOR', 'localhost'),
        busy_wait = int(getenv('BUSY_WAIT', 0)),
        window = int(getenv('WINDOW', 10)),
    )
    main(**kwargs)
