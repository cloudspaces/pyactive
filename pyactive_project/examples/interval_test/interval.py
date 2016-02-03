"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller, interval, interval_host, later

class Registry():
    _sync = {'hello_sync': '2'}
    _async = ['hello', 'init_start']
    _ref = []
    _parallel = []

    def __init__(self):
        self.names = {}

    def init_start(self):
        self.interval1 = interval_host(self._host, 1, self.hello)
        later(10, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()

    def hello(self):
        print 'Hello'

    def hello_sync(self):
        return 'hello_sync'



def test3():

    tcpconf = ('tcp',('127.0.0.1',1234))
    host = init_host(tcpconf)

    registry = host.spawn_id('1','interval','Registry',[])
    registry.init_start()

def main():
    start_controller('pyactive_thread')
    serve_forever(test3)

if __name__ == "__main__":
    main()
