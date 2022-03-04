from flask import Flask, request, jsonify
import logging
from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1
from os import getenv



class Processor:
    def __init__(self):
        self.elements = {}
        self.locations = {}
    def listen(self, id, data):
        if self.elements.get(id) is None:
            self.elements[id] = []
            self.locations[id] = data['location']
        self.elements[id].append(data)
        # print(self.elements)
    def list_id(self, id):
        data = self.elements.get(int(id))
        if data is None:
            return "No such id"
        return jsonify(data)
    def list_location(self, location):
        data = [self.elements[id] for id in self.locations.keys()
                if self.locations[id]==location]
        return jsonify(data)


a = Processor()
app = Flask(__name__)

@app.route('/listen', methods = ['POST'])
def listen():
    logging.info('Enter')
    data = request.get_json()
    data['timestamp_processed'] = time()
    id = int(data['id'])
    print(data)
    a.listen(id, data)
    # print(a.elements)
    return {}

@app.route('/data', methods = ['POST','GET'])
def data():
    id = request.args.get('id')
    location = request.args.get('location')
    if id is not None:
        return a.list_id(id)
    elif location is not None:
        return a.list_location(location)
    return "error"


def main(port):
    app.run(port=port, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    kwargs = dict(
            port = int(getenv('PORT', 5001)),
    )
    main(**kwargs)
