"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from chord_protocol import Node, k, SuccessorError
from pyactive.exception import TimeoutError

class ImprovedNode(Node):
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2'
             ,'join':'20', 'is_alive':'2', 'get_finger':'2', 'find_predecessor':"2"}
    _async = ['leave','set_predecessor', 'set_successor', 'show_finger_node', 'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor', 'get_predecessor', 'successor', 'find_successor', 'closest_preceding_finger', 'join',
            'set_successor', 'notify','get_finger', 'find_predecessor']
    _parallel = ['stabilize', 'fix_finger']


    def get_finger(self):
        return self.finger.values()

    def fix_finger(self):
        try:
            for i in range(4):
                if(self.currentFinger <= 0 or self.currentFinger >= k ):
                    self.currentFinger = 1
                self.finger[self.currentFinger] = self.find_successor(self.start[self.currentFinger])
                self.currentFinger += 1
        except:
            None

    def init_finger_table(self, n1):
        try:
            self.finger[0] = n1.find_successor(self.start[0])
            self.predecessor = self.finger[0].get_predecessor()
        except SuccessorError:
            raise
        except TimeoutError:
            raise
        else:
            neighbor_finger = self.finger[0].get_finger()
            for i in range(k - 1):
                self.finger[i + 1] = neighbor_finger[i]
