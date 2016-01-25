"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import launch,init_host, start_controller

def test_remote_spawn():
    tcpconf = ('tcp',('127.0.0.1',1240))
    host = init_host(tcpconf)
    remote_aref = 'tcp://127.0.0.1:1232/atom/Host/0'
    remote_host = host.lookup(remote_aref)
    remote_host.hello()
    print remote_host
    server = remote_host.spawn('s1','Server',[])
    z = server.add(6,7)
    print z
    server.substract(6,5)
    t = server.add(8,7)
    print t




def main():
    start_controller('pyactive_thread')
    launch(test_remote_spawn)

if __name__ == "__main__":
    main()
