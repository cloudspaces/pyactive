"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller

class Test():

    _sync = {'get_name': '1', 'registry_obj':'2'}
    _async = ['hello_world']
    _ref = []
    _parallel = []

    def __init__(self):
        self.name = None

    def hello_world(self):
        print 'async done'

    def get_name(self):
        return self.name

    def registry_obj(self, obj):
        self.obj = obj
        return True

def test3():

#    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host()

    test = host.spawn_id('1','launch','Test',[])
    test.hello_world()

if __name__ == "__main__":
    start_controller('pyactive_thread')
    launch(test3)
