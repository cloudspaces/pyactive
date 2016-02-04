"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch,start_controller, sleep
from pyactive.exception import TimeoutError

class Echo:
    _sync = {'get_msgs':1}
    _async = ['echo']
    _parallel = []
    _ref = []


    def __init__(self):
        self.msgs = []

    def echo(self,msg):
        print msg
        self.msgs.append(msg)

    def get_msgs(self):
        sleep(3)
        return self.msgs

def test():
    host = init_host()

    e1 = host.spawn_id('1', 'actor3c', 'Echo', [])

    e1.echo('hola')
    e1.echo('bon dia')
    e1.echo('adeu')


    try:
        msgs = e1.get_msgs()
    except TimeoutError as e:
        print e
    else:
        print msgs




if __name__ == '__main__':
    start_controller('pyactive_thread')
    launch(test)
