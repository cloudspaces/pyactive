
"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch,start_controller, sleep, serve_forever

class NotFound(Exception):pass
class AlreadyExists(Exception):pass

class Registry:
    _sync = {'get_all':1,'bind':1,'lookup':1,'bind':1,'unbind':1}
    _async = []
    _parallel = []
    _ref = ['get_all','bind','lookup']


    def __init__(self):
        self.actors = {}

    def bind(self,name,actor):
        if self.actors.has_key(name):
            raise AlreadyExists()
        else:
            self.actors[name] = actor


    def unbind(self,name):
        if self.actors.has_key(name):
            del self.actors[name]
        else:
            raise NotFound()

    def lookup(self,name):
        return self.actors[name]

    def get_all(self):
        return self.actors.values()


def test():
    tcpconf = ('tcp',('127.0.0.1',1232))
    host = init_host(tcpconf)
    registry = host.spawn_id('1', 'registry', 'Registry', [])

    print 'host listening in port 1232'


if __name__ == '__main__':
    start_controller('pyactive_thread')
    serve_forever(test)
