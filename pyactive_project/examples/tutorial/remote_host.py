"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import launch,init_host, start_controller


class Server():
    _sync = {'add': '1', 'wait_a_lot': '1'}
    _async = ['substract']
    _ref = []
    _parallel = []

    def add(self,x,y):
        return x+y

    def substract(self,x,y):
        print 'subtract',x-y

    def wait_a_lot(self):
        sleep(2)
        return 'ok'




def test_remote_spawn():
    tcpconf = ('tcp',('127.0.0.1',1240))
    host = init_host(tcpconf)
    remote_aref = 'tcp://127.0.0.1:1232/controller/Host/0'
    remote_host = host.lookup(remote_aref)
    print remote_host
    server = remote_host.spawn_id('0','remote_host','Server',[])
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
