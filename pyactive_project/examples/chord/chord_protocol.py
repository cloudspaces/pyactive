"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from pyactive.controller import init_host, serve_forever, start_controller, interval_host, sleep
from pyactive.exception import TimeoutError, PyactiveError


k = 6
MAX = 2 ** k


def decr(value, size):
    if size <= value:
        return value - size
    else:
        return MAX - (size - value)

#---------BETWEEN---------#
def between(value, init, end):
    if init == end:
        return True
    elif init > end :
        shift = MAX - init
        init = 0
        end = (end + shift) % MAX
        value = (value + shift) % MAX
    return init < value < end

def Ebetween(value, init, end):
    if value == init:
        return True
    else:
        return between(value, init, end)

def betweenE(value, init, end):
    if value == end:
        return True
    else:
        return between(value, init, end)

#-------END_BETWEEN-------#

def update(ref):
    ref.stabilize()
    ref.fix_finger()

def exit1(ref):
    ref.leave()

def show(ref):
    ref.show_finger_node()

class SuccessorError(PyactiveError):
    def __str__(self):
        return 'The successor is down'

class Node(object):
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2'
             ,'join':'20', 'is_alive':'2', 'find_predecessor':"2"}
    _async = ['leave','set_predecessor', 'set_successor', 'show_finger_node', 'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor', 'get_predecessor', 'successor', 'find_successor', 'closest_preceding_finger', 'join',
            'set_successor', 'notify', 'find_predecessor']
    _parallel = ['stabilize', 'fix_finger', 'find_predecessor']

    def __init__(self):
        self.finger = {}
        self.start = {}
        self.indexLSucc = 0
        self.currentFinger = 1

    def init_node(self):
        for i in range(k):
            self.start[i] = (long(self.id) + (2 ** i)) % (2 ** k)
        return True

    def successor(self):
        return self.finger[0]

    def find_successor(self, id):
        try:
            if betweenE(id, long(self.predecessor.get_id()), long(self.id)):
                return self.proxy
            n = self.find_predecessor(id)
            return n.successor()
        except TimeoutError:
            raise

    def get_predecessor(self):
        return self.predecessor

    def set_predecessor(self, pred):
        self.predecessor = pred

    #Iterative programming
    def find_predecessor(self, id):
        try:
            if id == long(self.id):
                return self.predecessor
            n1 = self.proxy
            while not betweenE(id, long(n1.get_id()), long(n1.successor().get_id())):
                n1 = n1.closest_preceding_finger(id)
            return n1
        except SuccessorError:
            raise
        except TimeoutError:
            raise

    def closest_preceding_finger(self, id):
        try:
            for i in range(k - 1, -1, -1):
                if between(long(self.finger[i].get_id()), long(self.id), id):
                    return self.finger[i]
            return self.proxy
        except(TimeoutError):
            raise SuccessorError()

    def join(self, n1):
        """if join return false, the node not entry in ring. Retry it before"""
        if self.id == n1.get_id():
            for i in range(k):
                self.finger[i] = self.proxy
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
                self.run = True
                return True

    def init_finger_table(self, n1):
        try:
            self.finger[0] = n1.find_successor(self.start[0])
            self.predecessor = self.finger[0].get_predecessor()
        except SuccessorError:
            raise
        except TimeoutError:
            raise
        else:
            for i in range(k - 1):
                self.finger[i + 1] = self.finger[0]

    def is_alive(self):
        if self.run:
            return True
        else:
            return False

    def stabilize(self):
        try:
            x = self.finger[0].get_predecessor()
        except:
            None
        else:
            if(between(long(x.get_id()), long(self.id), long(self.finger[0].get_id()))):
                self.set_successor(x)
            self.finger[0].notify(self.proxy)

    def notify(self, n):
        if(self.predecessor.get_id() == self.id or
           between(long(n.get_id()), long(self.predecessor.get_id()), long(self.id))):

            self.predecessor = n

    def fix_finger(self):
        try:
            if(self.currentFinger <= 0 or self.currentFinger >= k ):
                self.currentFinger = 1
            self.finger[self.currentFinger] = self.find_successor(self.start[self.currentFinger])
        except:
            None
        else:
            self.currentFinger += 1

    def leave(self):
        print 'bye bye!'
        self.finger[0].set_predecessor(self.predecessor)
        self.predecessor.set_successor(self.finger[0])
        self._atom.stop()

    def set_successor(self, succ):
        self.finger[0] = succ

    def show_finger_node(self):
        print 'Finger table of node ' + self.id
        print 'Predecessor' + self.predecessor.get_id()
        print 'start: node'
        for i in range(k):
            print str(self.start[i]) + ' : ' + self.finger[i].get_id()
        print '-----------'


def save_log(ref):
    ref.to_uml('chord_test2')
