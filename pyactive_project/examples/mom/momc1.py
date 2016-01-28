"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""

from pyactive.controller import init_host, launch, serve_forever,  start_controller, sleep
from pyactive.exception import TimeoutError
class Client():
    _sync = {'send_add': '1'}
    _async = ['send_substract']
    _ref = []
    _parallel = []

    def __init__(self, server):
        self.server = server


    def send_add(self, num1, num2):
        return self.server.add(num1, num2)


    def send_substract(self, num1, num2):
        self.server.substract(num1, num2)


def test3():
    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    #host = init_host(('127.0.0.1',4329),True)
    #host = Host(host)
    #oref = 'env2:simple:s1:Server'
    aref = 'mom://s1/moms1/Server/0'
    ref = host.lookup(aref)

    n1 = host.spawn_id('c1', 'momc1', 'Client', [ref])
    #for i in range(100):
    #    ref.resta(34,2)

    n1.send_substract(34,2)
    print n1.send_add(6,8)
    for i in range(3):
        s = n1.send_add(56,4)
        print s,'ok'
#    try:
#        ref.wait_a_lot()
#    except TimeoutError:
#        print 'correct timeout'

    #sleep(1)


def main():
    start_controller("pyactive_thread")
    launch(test3)
    #test1()

if __name__ == "__main__":
    main()
