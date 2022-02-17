from argparse import ArgumentParser
from requests import post
from time import time, sleep
from math import sin, pi
from random import uniform
from hashlib import sha1

DAY = 86400


def hash(string):
    return int(sha1(string.encode('utf-8')).hexdigest(), 16)


class Processor:
    def __init__(self, ip, port):
        self.ip = ip
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
        self.processor = Processor('127.0.0.1', 5000)
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
        post(self.processor.url(), json={
            'id': self.id,
            'location': self.location,
            'temperature': temp,
            'timestamp': time(),
        })


def main(processor, port, location, interval, id):
    g = Generator()
    g.processor = Processor(processor, port)
    g.location = location
    g.interval = interval
    g.id = id

    while True:
        g.post()
        sleep(g.interval)



if __name__ == "__main__":
    q = ArgumentParser(description='ASPS Generator')
    q.add_argument(
        '-p',
        '--processor',
        metavar = 'IP:PORT',
        type = str,
        default = '127.0.0.1:5000',
        help = 'Processor to post data'
    )
    q.add_argument(
        '-l',
        '--location',
        metavar = 'LOCATION',
        type = str,
        default = 'Athens',
        help = 'Generator location'
    )
    q.add_argument(
        '-i',
        '--id',
        type = int,
        default = 1,
        help = 'Generator unique id'
    )
    q.add_argument(
        '-t',
        '--interval',
        type = int,
        default = 1,
        help = 'Post interval'
    )
    kwargs = vars(q.parse_args())
    kwargs['processor'], kwargs['port'] = kwargs['processor'].split(':')
    main(**kwargs)
