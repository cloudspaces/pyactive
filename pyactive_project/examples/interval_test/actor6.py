
from pyactive.controller import init_host, launch, serve_forever,start_controller, sleep

class File:
   _sync = {'download':10}
   _async = []
   _parallel = []
   _ref = []

   def download(self,filename):
       print 'downloading '+ filename
       sleep(5)
       return True

class Web:
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

class Workload:
   _sync = {}
   _async = ['launch','download', 'remote_server']
   _parallel = []
   _ref = ["remote_server"]

   def launch(self):
    #    for i in range(10):
    #        print 'contador', i
        #    try:
      print self.server.list_files()
        #    except Exception, e:
        #        print e
   def remote_server(self, web_server):
       self.server = web_server

   def download(self):
       print self.server.get_file('a1.txt')


def test():
   host = init_host()

   # parameters 1 = 'id', 'test_sync' = module name, 'Server' = class name
   # f1 = host.spawn_id('1', 'actor6', 'File', [])
   web = host.spawn_id('2', 'actor6', 'Web', [])
   load = host.spawn_id('3', 'actor6', 'Workload', [])
   load.remote_server(web)
   # load2 = host.spawn_id('4', 'actor6', 'Workload', [])
   # load2.remote_server(web)
   sleep(2)
   load.launch()
   # load2.download()


if __name__ == '__main__':
#you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
   start_controller('pyactive_thread')
   serve_forever(test)
