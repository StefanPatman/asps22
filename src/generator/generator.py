from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1
from os import getenv
from socket import gethostbyname

DAY = 86400


def hash(string):
    return int(sha1(string.encode('utf-8')).hexdigest(), 16)


class Aggregator:
    def __init__(self, host, port):
        self.ip = gethostbyname(host)
        self.port = port
        self.route = 'listen'

    def url(self):
        return f'http://{self.ip}:{self.port}/{self.route}'


class Generator:

    TEMP_MAX = 40
    TEMP_MIN = -10
    DIV_MAX = 10
    DIV_MIN = -10
    RND_MAX = 2
    RND_MIN = -2
    FACTOR = 10

    def __init__(self):
        self.aggregator = Aggregator('127.0.0.1', 5000)
        self.location = 'Athens'
        self.interval = 1  # seconds
        self.id = 1

    def temperature(self):
        loc = hash(self.location) % (self.TEMP_MAX - self.TEMP_MIN)
        div = hash(str(self.id)) % (self.DIV_MAX - self.DIV_MIN)
        sec = time() % DAY
        off = self.FACTOR * sin(2*pi*sec/DAY)
        rnd = uniform(self.RND_MIN, self.RND_MAX)
        return loc + div + off + rnd

    def post(self):
        temp = self.temperature()
        print(temp)
        post(self.aggregator.url(), json={
           'id': self.id,
           'location': self.location,
           'temperature': temp,
           'timestamp_sent': time(),
        })


def main(aggregator, port, location, interval, id):
    g = Generator()
    g.aggregator = Aggregator(aggregator, port)
    g.location = location
    g.interval = interval
    g.id = id
    while True:
        try:
            g.post()
        except Exception:
            print('Failed to connect')
        sleep(g.interval)



if __name__ == "__main__":
    kwargs = dict(
            port = int(getenv('PORT', 5000)),
            aggregator = getenv('AGGREGATOR', 'localhost'),
            location = getenv('LOCATION', 'Athens'),
            interval = int(getenv('INTERVAL', 1)),
            id = int(getenv('ID', 1)),
    )
    main(**kwargs)
