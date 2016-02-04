"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller


def test():
    tcpconf = ('tcp',('127.0.0.1',1232))
    host = init_host(tcpconf)
    print 'host listening in port 1232'


if __name__ == '__main__':
    start_controller('pyactive_thread')
    serve_forever(test)
