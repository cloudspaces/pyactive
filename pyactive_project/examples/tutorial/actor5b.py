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

class Bot:
    _sync = {}
    _async = ['insult','set_channel']
    _parallel = []
    _ref = []

    def __init__(self):
        self.insults = ['stupid','silly','dumb','arrogant']

    def insult(self):
        for insult in self.insults:
            self.channel.echo(insult)

    def set_channel(self):
        self.channel = self.host.lookup('atom://local/actor5b/Echo/1')

def test():
    host = init_host()
    e1 = host.spawn_id('1', 'actor5b', 'Echo', [])
    bot = host.spawn_id('1', 'actor5b', 'Bot', [])
    bot.set_channel()
    bot.insult()
    sleep(4)

if __name__ == '__main__':
    start_controller('pyactive_thread')
    launch(test)
