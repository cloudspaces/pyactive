"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import sys

from pyactive.controller import init_host, launch, start_controller,sleep

from time import time
<<<<<<< .mine
NUM_NODES = 50000
NUM_MSGS = 100
=======
NUM_NODES = 100
NUM_MSGS = 10000
>>>>>>> .r70

class Node():
<<<<<<< .mine
    _sync = {'is_finished':'1'}
    _async = ['set_next', 'init_token', 'take_token']
    _ref = ['set_next']
    _parallel = []
    
=======
    _sync = {'is_finished': '1', 'get_cnt': '1'}
    _async = ['init_token', 'take_token', 'set_next']
    _ref = ['set_next']
    _parallel = []
    
>>>>>>> .r70
    def __init__(self,id=None,next=None):
        self.id = id
        self.next = next  
        self.cnt = 0


    def set_next(self, n2):        
        self.next = n2
            

    def get_cnt(self):
        return self.cnt
    

    def is_finished(self):
        return self.cnt >= NUM_MSGS
    

    def init_token(self):
        #print 'send token',self,'->',self.next
        self.next.take_token()
        
    def take_token(self):
        self.cnt += 1
        if (not self.is_finished()):
            self.next.take_token()
        #print 'taken token',self.cnt
    
def testN():
    
    host = init_host()
    
    print 'TEST ',NUM_NODES,' nodes and', NUM_MSGS, "messages."
    
    nf  = host.spawn_id('init', 'ring3','Node',['nf'])
    
    ni = nf;
    for i in range (NUM_NODES-2):    
        ni = host.spawn_id(str(i), 'ring3','Node',[('n',i),ni]) 
    
    n1 = host.spawn_id('end','ring3','Node',['n1',ni]) 
        
    nf.set_next(n1)  
    print 'start time!!'
    init = time()
      
    nf.init_token()
  
    while(not n1.is_finished()):
        sleep(0.01)
        
    end = time()   
    
    print ((end - init)*1000),' ms.' 
    
 
def main():
    start_controller('tasklet')
    launch(testN)
    print 'finish!'
 
if __name__ == "__main__":
    main() 
  