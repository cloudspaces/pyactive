"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
        Edgar Zamora-Gómez <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller, launch

def test3():
    tcpconf = ('tcp',('127.0.0.1',1259))
    host = init_host(tcpconf)

    registry = host.lookup('tcp://127.0.0.1:6664/first/Registry/1')

    registry.bind('third', host)


def main():
    start_controller('pyactive_thread')
    serve_forever(test3)

if __name__ == "__main__":
    main()
