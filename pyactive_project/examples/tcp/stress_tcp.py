"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller
import sys
from time import time

def test3():
    host = init_host(('tcp',('127.0.0.1',1235)))
    #host = init_host(('127.0.0.1',4322),True)
    #host = Host(host)
    #oref = 'env2:simple:s1:Server'
    aref = 'tcp://127.0.0.1:1234/s1/Server/0'
    ref = host.lookup(aref)

    init = time()
    for i in range (10000):
        ref.substract(6,7)
    end = time()

    print end - init


def main():
    start_controller('pyactive_thread')
    launch(test3)
    #test1()

if __name__ == "__main__":
    main()
