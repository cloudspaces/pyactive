"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch, serve_forever,start_controller, sleep
from pyactive.exception import TimeoutError

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
    _async = ['launch','remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        for i in range(5):
            print self.server.get_file(i)

    def remote_server(self, web_server):
        self.server = web_server



def test():
    host = init_host()

    # parameters 1 = 'id', 'test_sync' = module name, 'Server' = class name
    web = host.spawn_id('1', 'actor10', 'Web', [])
    load = host.spawn_id('1', 'actor10', 'Workload', [])
    load.remote_server(web)
    load.launch()





if __name__ == '__main__':
#you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
    start_controller('pyactive_thread')
    launch(test)
