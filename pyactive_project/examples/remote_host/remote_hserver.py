"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import start_controller, init_host, serve_forever

def test():
    start_controller("pyactive_thread")
    tcpconf = ('tcp',('127.0.0.1',1232))
    host = init_host(tcpconf)


def main():
    #test3(sys.argv[1])
    start_controller("pyactive_thread")
    serve_forever(test)

if __name__ == "__main__":
    main()
