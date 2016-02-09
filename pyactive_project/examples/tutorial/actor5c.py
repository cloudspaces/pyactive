"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, launch,start_controller, sleep

class Echo:
    _sync = {}
    _async = ['echo']
    _parallel = []
    _ref = ['echo']

    def echo(self,msg,sender):
        print msg,'from:',sender.get_name()

class Bot:
    _sync = {'get_name':1}
    _async = ['insult','set_channel']
    _parallel = []
    _ref = []

    def __init__(self):
        self.insults = ['stupid','silly','dumb','arrogant']

    def get_name(self):
        return 'bot'+self.id

    def insult(self):
        for insult in self.insults:
            self.channel.echo(insult,self.proxy)

    def set_channel(self):
        self.channel = self.host.lookup('atom://local/actor5c/Echo/1')

def test():
    host = init_host()
    e1 = host.spawn_id('1', 'actor5c', 'Echo', [])
    bot = host.spawn_id('1', 'actor5c', 'Bot', [])
    bot.set_channel()
    bot.insult()
    sleep(4)

if __name__ == '__main__':
    start_controller('pyactive_thread')
    launch(test)
