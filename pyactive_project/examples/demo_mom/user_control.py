'''
Created on 14/07/2014

@author: edgar
'''
from pyactive.controller import init_host, launch, serve_forever,  start_controller, sleep, interval
from pyactive.exception import TimeoutError

start_controller("pyactive_thread")

momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
host = init_host(momconf)
#host = init_host(('127.0.0.1',4329),True)
#host = Host(host)
#oref = 'env2:simple:s1:Server'
aref = 'mom://s1/server/Server/0'
ref = host.lookup(aref)

ref.run_clients()
