"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch,start_controller, sleep


class Echo:
    _sync = {}
    _async = ['echo']
    _parallel = []
    _ref = []

    def echo(self,msg):
        print msg

def test():
    host = init_host()
    e1 = host.spawn_id('1', 'actor1', 'Echo', [])

    e1.echo('hola')
    e1.echo('adios')




if __name__ == '__main__':
    start_controller('pyactive_thread')
    launch(test)
