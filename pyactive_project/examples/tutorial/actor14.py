"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import launch,init_host, start_controller
from registry import NotFound

def test_remote_spawn():
    tcpconf = ('tcp',('127.0.0.1',1242))
    host = init_host(tcpconf)
    remote_aref = 'tcp://127.0.0.1:1232/registry/Registry/1'
    registry= host.lookup(remote_aref)
    remote_host = registry.lookup('host1')




    server = remote_host.spawn_id('0','remote_host','Server',[])
    z = server.add(6,7)
    print z
    server.substract(6,5)
    t = server.add(8,7)
    print t

    try:
        registry.unbind('pepe')
    except NotFound:
        print "Cannot unbind this object"



def main():
    start_controller('pyactive_thread')
    launch(test_remote_spawn)

if __name__ == "__main__":
    main()
