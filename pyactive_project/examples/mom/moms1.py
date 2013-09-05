"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller, sleep
class Server:
    _sync = {'add': '1', 'wait_a_lot':'1'}
    _async = ['substract']
    _ref = []
    _parallel = []
    
    def add(self,x,y):
        return x+y

    def substract(self,x,y):
        print 'substract',x-y
    
    def wait_a_lot(self):
        sleep(2)
        return 'ok'
   

    #channel.send({'timeout':'TRUE'})
def test3():
    momconf = ('mom',{'name':'s1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    #host = init_host(('127.0.0.1',1290),True)
    #host = Host(hostname)
    server = host.spawn_id('0','moms1','Server',[])
    server.substract(4,3)
    print server.add(66,7)
    #host.serve_forever()
   


def main():
    #test3(sys.argv[1])
    start_controller("pyactive_thread")
    serve_forever(test3)
    
if __name__ == "__main__":
    main()