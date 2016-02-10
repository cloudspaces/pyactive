"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from chord_protocol import Node, k, MAX, between, start_node, update, show
from chord_log import save_log
from pyactive.controller import serve_forever, start_controller, init_host, interval, sleep
from pyactive.exception import TimeoutError
import random, sys

I ={}
global sample
def id(MAX):
    # Returns a random number between 0 y 2^k (64)
    return int(random.uniform(1, MAX))

""" Uniform distribution of identifiers across the identifier space"""
def uniform(N, I, max):
    sample= []
    for next in range(N):
        tmp_id = id(max)
        # We are looking for an ID which does not exist in the network, because could happen that
        # the random function gives us an existing value.
        while tmp_id in I:
            tmp_id = id(max)
        # Once we are sure the value is unique, we store it in the identifier space dictionary
        I[tmp_id] = tmp_id
        # We add it to the list where we have the N identifiers of the uniformly found nodes
        sample.append(tmp_id)
    return sample

class SuccNode(Node):
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2'
             ,'join':'20', 'is_alive':'2','get_finger':'2', 'give_successor_list':'5', 'find_predecessor':"2"}
    _async = ['leave','set_predecessor', 'set_successor', 'show_finger_node', 'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor','get_finger', 'get_predecessor', 'successor', 'find_successor', 'closest_preceding_finger', 'join',
            'set_successor', 'notify', 'find_predecessor']
    _parallel = ['stabilize', 'fix_finger']

    def __init__(self):
        super(SuccNode, self).__init__()
        self.successorList = []
        self.retry = [0,0]

    def successor(self):
        return self.successorList[0]

    def join(self, n1):
        """if join return false, the node not entry in ring. Retry it before"""
        if self.id == n1.get_id():
            for i in range(k):
                self.finger[i] = self.proxy
                self.successorList.append(self.proxy)
            self.predecessor = self.proxy
            self.run = True
            return True
        else:
            try:
                self.init_finger_table(n1)
            except:
                print 'Join failed'
                return False
            else:
                self.init_successor_list()
                self.run = True
                return True

    def init_successor_list(self):
        self.successorList.append(self.finger[0])
        for i in range(k - 1):
            self.successorList.append(self.successorList[i].successor())

    def update_list_successor(self):
        try:
            if(self.successorList[0].is_alive()):
                auxList = self.successorList[0].give_successor_list()
                for i in range(k-1):
                    self.successorList[i+1] = auxList[i]
                self.retry[0] = 0
        except(TimeoutError):
            self.retry[0] += 1
            if self.retry[0] > 5:
                self.retry[0] = 0
                self.update_successor()

    def update_successor(self):
        searching = True
        while(searching and self.indexLSucc < k):
            n = self.successorList[self.indexLSucc]
            self.indexLSucc += 1
            self.successorList[0] = n
            try:
                if(n.is_alive()):
                    self.set_successor(n)
                    searching = False
            except(TimeoutError):
                searching = True
        self.indexLSucc = 1
        self.update_list_successor()

    def give_successor_list(self):
        return self.successorList[:]

    def stablilize(self):
        try:
            x = self.successorList[0].get_predecessor()
            self.retry[1] = 0
        except(TimeoutError):
            self.retry[1] += 1
            if self.retry[1] > 5:
                self.retry[1] = 0
                self.update_successor()

        else:
            if(between(int(x.get_id()), int(self.id), int(self.successorList[0].get_id()))):
                self.set_successor(x)
            self.update_list_successor()
            self.successorList[0].notify(self.proxy)

    def set_successor(self, succ):
        self.successorList[0] = succ
        super(SuccNode, self).set_successor(succ)

    def leave(self):
        print 'bye bye!'
        self.successorList[0].set_predecessor(self.predecessor)
        self.predecessor.set_successor(self.successorList[0])
        self._atom.stop()
