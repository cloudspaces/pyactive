"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller

class Registry():
    _sync = {'hello_sync': '2'}
    _async = ['hello']
    _ref = []
    _parallel = []

    def __init__(self):
        self.names = {}

    def hello(self):
        print 'Hello'

    def hello_sync(self):
        return 'hello_sync'



def test3():

    tcpconf = ('tcp',('127.0.0.1',1234))
    host = init_host(tcpconf)

    registry = host.spawn_id('1','server','Registry',[])


def main():
    start_controller('pyactive_thread')
    serve_forever(test3)

if __name__ == "__main__":
    main()
