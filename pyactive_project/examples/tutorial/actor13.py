"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import launch,init_host, start_controller,serve_forever



def test_registry():
    tcpconf = ('tcp',('127.0.0.1',1240))
    host = init_host(tcpconf)
    remote_aref = 'tcp://127.0.0.1:1232/registry/Registry/1'
    registry = host.lookup(remote_aref)
    registry.bind('host1',host)



def main():
    start_controller('pyactive_thread')
    serve_forever(test_registry)

if __name__ == "__main__":
    main()
