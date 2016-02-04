"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch, serve_forever,start_controller, sleep
from pyactive.exception import TimeoutError
class File(object):
    _sync = {'download':10}
    _async = []
    _parallel = []
    _ref = []

    def download(self,filename):
        print 'downloading ',filename
        sleep(5)
        return True

class Web(object):
    _sync = {'list_files':1,'get_file':10}
    _async = ['remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def __init__(self):
        self.files = ['a1.txt','a2.txt','a3.txt','a4.zip']
    def remote_server(self, file_server):
        self.server = file_server
    def list_files(self):
        return self.files

    def get_file(self,filename):
        return self.server.download(filename)

class Workload(object):
    _sync = {}
    _async = ['launch','download', 'remote_server']
    _parallel = []
    _ref = ["remote_server"]

    def launch(self):
        for i in range(10):
            """
            Without parallels the next line of code raise a TimeoutError exception. To handle
            the exception uncomment the try/except lines.
            """
         #    try:
            print self.server.list_files()
         #    except TimeoutError as e:
         #        print e

    def remote_server(self, web_server):
        self.server = web_server

    def download(self):
        self.server.get_file('a1.txt')
        print 'download finished'


def test():
    host = init_host()

    # parameters 1 = 'id', 'test_sync' = module name, 'Server' = class name
    f1 = host.spawn_id('1', 'actor8', 'File', [])
    web = host.spawn_id('1', 'actor8', 'Web', [])
    web.remote_server(f1)
    load = host.spawn_id('1', 'actor8', 'Workload', [])
    load.remote_server(web)
    load2 = host.spawn_id('2', 'actor8', 'Workload', [])
    load2.remote_server(web)
    load.launch()
    load2.download()


    sleep(10)


if __name__ == '__main__':
#you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
    start_controller('pyactive_thread')
    launch(test)
