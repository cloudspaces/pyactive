"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller, interval, later

class Echo():
    _sync = {}
    _async = ['echo']
    _ref = []
    _parallel = []

    def __init__(self):
        self.names = {}


    def echo(self, msg):
        print msg



def test3():

    tcpconf = ('tcp',('127.0.0.1',1234))
    host = init_host(tcpconf)

    registry = host.spawn_id('1','actor2','Echo',[])


def main():
    start_controller('pyactive_thread')
    serve_forever(test3)

if __name__ == "__main__":
    main()
