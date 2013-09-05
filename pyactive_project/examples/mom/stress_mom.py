"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""

from pyactive.controller import init_host, launch, start_controller, sleep
from time import time


def test3():
    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    #host = init_host(('127.0.0.1',4329),True)
    #host = Host(host)
    #oref = 'env2:simple:s1:Server'
    aref = 'mom://s1/moms1/Server/0'
    ref = host.lookup(aref)
 
    init = time()
    for i in range (10000):
        z = ref.add(6,7)
        print i 
    end = time()

    print end - init
    
    #sleep(3)
    host.shutdown()


def main():
    start_controller('pyactive_thread')
    launch(test3)
    #test1()
    
if __name__ == "__main__":
    main()