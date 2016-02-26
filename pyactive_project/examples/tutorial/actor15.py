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

    echos = []
    hosts = registry.get_all()
    for remote_host in hosts:
      echo = remote_host.spawn_id('1','actor1','Echo',[])
      echos.append(echo)

    for server in echos:
      server.echo('Hi !!!! I am controlling your machine !!!!!!!!!')



def main():
    start_controller('pyactive_thread')
    launch(test_remote_spawn)

if __name__ == "__main__":
    main()
