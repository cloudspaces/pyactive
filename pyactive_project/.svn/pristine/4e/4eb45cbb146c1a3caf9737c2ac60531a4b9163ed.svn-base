"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import unittest

from pyactive.controller import init_host, launch, start_controller, sleep


       
class Node():
 
    def __init__(self,id=None,n2=None):
        self.id = id
        self.now=False  
        self.next = n2  
        self.cnt = 0

#    @ref
    #@sync(1)
    def set_next(self, n2):        
        self.next = n2
        return True
            
    #@sync(1)
    def get_cnt(self):
        return self.cnt
    
    #@async
    def init_token(self):
        print 'send token',self,'->',self.next
        self.next.take_token()
        print 'finish'
        
    #@async
    def take_token(self):
        self.cnt += 1
        if (self.cnt<2):
            self.next.take_token()
        print 'taken token',self
                            

def test1(test):
    n3  = test.host.spawn_id('0','ring2','Node',['n3'])
    n2 = test.host.spawn_id('1','ring2','Node',['n2',n3]) 
    n1 = test.host.spawn_id('2','ring2','Node',['n1',n2]) 
    
    
    n3.set_next(n1)  
      
    n1.init_token()
    sleep(0.5)
    cnt = n3.get_cnt()
    
    test.assertEqual(cnt, 1, "testing message loop") 
    
def testN(test):
    
    nf  = test.host.spawn_id('3','ring2','Node',['nf'])
    
    ni = nf;
    for i in range (10):    
        ni = test.host.spawn_id(str(i + 4),'ring2','Node',[('n',i+4),ni]) 
    
    n1 = test.host.spawn_id('16','ring2','Node',['n1',ni]) 
        
    nf.set_next(n1)  
      
    n1.init_token()
    sleep(0.5)
    cnt = nf.get_cnt()
    
    test.assertEqual(cnt, 1, "testing message loop")     

class Simple(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        start_controller('tasklet')
        self.host = init_host()
        #self.host = Host('pedro')
         
    def test_load_oneway(self):
        launch(test1,[self])
        launch(testN,[self])
        
    def tearDown(self):
        self.host.shutdown()
      
    def tearDownModule(self):
        sleep(0.2)
      
if __name__ == '__main__':
    unittest.main()