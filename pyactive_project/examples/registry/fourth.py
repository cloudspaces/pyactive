"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
        Edgar Zamora-Gómez <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, launch,  start_controller



def test3():
    tcpconf = ('tcp',('127.0.0.1',1236))
    host = init_host(tcpconf)

    registry = host.lookup('tcp://127.0.0.1:6664/first/Registry/1')

    registry.bind('fourth', host)

    for atom in registry.get_values():
        print atom.get_aref()

def main():
    start_controller('pyactive_thread')
    launch(test3)

if __name__ == "__main__":
    main()
