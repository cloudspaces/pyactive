'''
Created on 14/07/2014

@author: Edgar Zamora Gomez
'''
from pyactive.controller import init_host, serve_forever, start_controller, sleep
from pyactive.Multi import AMulti
import random

class Server:
    _sync = {'add_client': '1', 'delete_client':'1', 'get_references':'1'}
    _async = ['do_something', 'run_clients', 'stop_clients']
    _ref = ['add_client', 'delete_client']
    _parallel = []
    
    def __init__(self):
        print 'hola'
        self.references = [x for x in range(1000)]
        self.amulti = AMulti()
        print self.references
    def add_client(self, client):
        self.amulti.attach(client)
        return self.references.pop()
    def delete_client(self, client):
        self.amulti.detach(client)
        return True
    def do_something(self, param):
        print 'Params: ', param
    def run_clients(self):
        self.amulti.run()
    def stop_clients(self):
        self.amulti.stop()
    def get_references(self):
        return self.references
   
                            
    #channel.send({'timeout':'TRUE'})
def test3():
    momconf = ('mom',{'name':'s1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test_edgar'})
    host = init_host(momconf)
    #host = init_host(('127.0.0.1',1290),True)
    #host = Host(hostname)
    server = host.spawn_id('0','server','Server',[])
    print 'Server running...'
    #host.serve_forever()
   

def main():
    #test3(sys.argv[1])
    start_controller("pyactive_thread")
    serve_forever(test3)
    
if __name__ == "__main__":
    main()