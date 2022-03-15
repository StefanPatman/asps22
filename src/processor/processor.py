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

    def exists(self, id):
        return (int(id) in self.elements.keys())

    def history(self, id):
        data = self.elements.get(int(id))
        if data is None:
            return f"No such id: {id}"
        return list(data)

a = Processor()
app = Flask(__name__)


@app.route('/listen', methods = ['POST'])
def listen():
    data = request.get_json()
    data['timestamp_arrived'] = time()
    id = int(data['id'])
    a.listen(id, data)
    return {}

@app.route('/history/all', methods = ['GET'])
def history_all():
    app.logger.info(f'All history')
    return jsonify({
        id: a.history(id) for id in a.elements.keys()
    })

@app.route('/history/generator', methods = ['GET'])
def history_generator():
    ids = request.args.getlist('id')
    app.logger.info(f'History for IDs: {repr(ids)}')
    if ids is None:
        return "Missing argument: id"
    return jsonify({
        id: a.history(id) for id in ids
    })

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

#
# /latest/all
# /latest/floor?id=1&id=2
# /latest/generator?id=1
# /maximum/all
# /maximum/floor?id=1&id=2
# /maximum/generator?id=1
# /history/all
# /history/generator?id=1
# /history/graph?id=1
#

def main(port):
    app.run(port=port, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    kwargs = dict(
            port = int(getenv('PORT', 5001)),
    )
    main(**kwargs)
