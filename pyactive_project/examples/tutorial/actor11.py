"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch, serve_forever,start_controller, sleep, interval_host, later
from pyactive.exception import TimeoutError
import random

class Web(object):
    _sync = {'list_files':1,'get_file':1}
    _async = []
    _parallel = []
    _ref = []

    def __init__(self):
        self.files = ['a1.txt','a2.txt','a3.txt','a4.zip']

    def list_files(self):
        return self.files

    def get_file(self,index):
        if index<len(self.files):
            return self.files[index]
        else:
            return '404 No File Found'

class Workload(object):
    _sync = {}
    _async = ['launch','remote_server','start_interval','stop_interval']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        index = random.randint(0,5)
        print self.server.get_file(index)


    def start_interval(self):
        self.interval1 = interval_host(self._host, 2, self.launch)
        later(15, self.stop_interval)

    def stop_interval(self):
        self.interval1.set()
        self._host.shutdown()

    def remote_server(self, web_server):
        self.server = web_server



def test():
    host = init_host()
    web = host.spawn_id('1', 'actor11', 'Web', [])
    load = host.spawn_id('1', 'actor11', 'Workload', [])
    load.remote_server(web)
    load.start_interval()



if __name__ == '__main__':
    start_controller('pyactive_thread')
    serve_forever(test)
