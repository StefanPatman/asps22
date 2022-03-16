from flask import Flask, request, jsonify, Response
import logging
from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1
from collections import deque
from os import getenv


class Processor:
    def __init__(self):
        self.history_length = 10
        self.elements = {}
        self.locations = {}

    def listen(self, id, data):
        if self.elements.get(id) is None:
            self.elements[id] = deque(maxlen=self.history_length)
            self.locations[id] = data['location']
        self.elements[id].append(data)

    def ids(self):
        return self.elements.keys()

    def exists(self, id):
        return (int(id) in self.elements.keys())

    def is_in_location(self, id, location):
        return (self.locations[id] == location)

    def history(self, id):
        data = self.elements.get(int(id))
        if data is None:
            return f"No such id: {id}"
        return list(data)

    def latest(self, id):
        data = self.elements.get(int(id))
        if data is None:
            return f"No such id: {id}"
        return data[-1]

    def maximum(self, id):
        data = self.elements.get(int(id))
        if data is None:
            return f"No such id: {id}"
        return max(data, key=lambda x: x['temperature'])

    def aggregate(self, id, attr):
        data = self.elements.get(int(id))
        if data is None:
            return f"No such id: {id}"
        s = sum(x[attr] for x in data)
        l = len(data)
        return s / l

    def delay(self, id):
        return self.aggregate(id, 'delay')

    def computation(self, id):
        return self.aggregate(id, 'computation')


a = Processor()
app = Flask(__name__)


@app.route('/listen', methods = ['POST'])
def listen():
    data = request.get_json()
    data['timestamp_arrived'] = time()
    data['delay'] = time() - data['timestamp_last_generated']
    data['computation'] = data['timestamp_computed'] - data['timestamp_last_aggregated']
    id = int(data['id'])
    a.listen(id, data)
    return {}


def attr_generator_id(ids, attr):
    return jsonify({
        id: getattr(a, attr)(id) for id in ids
    })


def attr_generator_location(locations, attr):
    ids = [id for id in a.ids() if any(a.is_in_location(id, loc) for loc in locations)]
    return jsonify({
        id: getattr(a, attr)(id) for id in ids
    })


def attr_generator(attr):
    ids = request.args.getlist('id')
    locations = request.args.getlist('location')
    if ids:
        return attr_generator_id(ids, attr)
    elif locations:
        return attr_generator_location(locations, attr)
    return "Missing argument: id or location"


def attr_all(attr):
    return jsonify({
        id: getattr(a, attr)(id) for id in a.ids()
    })


@app.route('/latest', methods = ['GET'])
def latest_generator():
    return attr_generator('latest')


@app.route('/latest/all', methods = ['GET'])
def latest_all():
    return attr_all('latest')


@app.route('/maximum', methods = ['GET'])
def maximum_generator():
    return attr_generator('maximum')


@app.route('/maximum/all', methods = ['GET'])
def maximum_all():
    return attr_all('maximum')


@app.route('/history', methods = ['GET'])
def history_generator():
    return attr_generator('history')


@app.route('/history/all', methods = ['GET'])
def history_all():
    return attr_all('history')


@app.route('/delay', methods = ['GET'])
def delay_generator():
    return attr_generator('delay')


@app.route('/delay/all', methods = ['GET'])
def delay_all():
    return attr_all('delay')


@app.route('/computation', methods = ['GET'])
def computation_generator():
    return attr_generator('computation')


@app.route('/computation/all', methods = ['GET'])
def computation_all():
    return attr_all('computation')


@app.route('/graph', methods = ['GET'])
def graph():
    id = request.args.get('id')
    app.logger.info(f'Graph for ID: {repr(id)}')
    if id is None:
        return "Missing argument: id"
    if not a.exists(id):
        return f"No such id: {id}"
    return jsonify({
        x['timestamp_last_generated']: x['temperature']
        for x in a.history(id)
    })


def main(port, history_length):
    a.history_length = history_length
    app.run(port=port, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    kwargs = dict(
        port = int(getenv('PORT', 5001)),
        history_length = int(getenv('HISTORY_LENGTH', 10)),
    )
    main(**kwargs)
