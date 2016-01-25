"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller, sleep
from pyactive.exception import TimeoutError


def test3():
    host = init_host(('tcp',('127.0.0.1',4346)))
    aref = 'tcp://127.0.0.1:1234/s1/Server/0'
    ref = host.lookup(aref)
    ref.substract(34,2)
    ref.add(6,8)
    for i in range(3):
        s = ref.add(56,4)
        print s,'ok'
    sleep(1)
    try:
        ref.wait_a_lot()
    except TimeoutError:
        print 'correct timeout'
        
    sleep(3)
    host.shutdown()

def main():
    start_controller('pyactive_thread')
    launch(test3)

if __name__ == "__main__":
    main()
