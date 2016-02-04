"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, serve_forever,start_controller, sleep

class Echo:
    _sync = {}
    _async = ['echo']
    _parallel = []
    _ref = []

    def echo(self,msg):
        print msg

def test():
    tcpconf = ('tcp',('127.0.0.1',1237))
    host = init_host(tcpconf)

    e1 = host.spawn_id('1', 'actor2', 'Echo', [])



if __name__ == '__main__':
    start_controller('pyactive_thread')
    serve_forever(test)
