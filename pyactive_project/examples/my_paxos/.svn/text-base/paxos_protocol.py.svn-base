'''
Created on 29/10/2013

@author: Edgar Zamora Gomez
'''
import collections
from pyactive.Multi import SMulti, AMulti
ProposalID = collections.namedtuple('ProposalID', ['number', 'uid'])

class Proposer (object):
    _sync = {}
    _async = ['set_multi', 'prepare', 'promise', 'set_proposal']
    _ref = ['set_multi']
    _parallel = []
    

    def __init__(self,  quorum_size):
        self.quorum_size = quorum_size
        self.proposed_value       = None
        self.last_accepted_id     = None
        self.next_proposal_number = 1
    #async, ref
    def set_multi(self, list_acceptors):
        self.list_acceptors = list_acceptors
        self.amulti = AMulti(self.list_acceptors)
        
    def set_proposal(self, value):
        '''
        Sets the proposal value for this node if this node is not already aware of
        another proposal having already been accepted. 
        '''
        if self.proposed_value is None:
            self.proposed_value = value


    def prepare(self):
        '''
        Sends a prepare request to all Acceptors as the first step in attempting to
        acquire leadership of the Paxos instance. 
        '''
        self.promises_rcvd = set()
        self.proposal_id   = ProposalID(self.next_proposal_number, self.id)
        self.next_proposal_number += 1
        #multi to all acceptors!! 
        self.amulti.onPrepare(self.proxy, self.proposal_id)

    
    def promise(self, from_uid, proposal_id, prev_accepted_id, prev_accepted_value):
        '''
        Called when a Promise message is received from an Acceptor
        '''

        # Ignore the message if it's for an old proposal or we have already received
        # a response from this Acceptor
        if proposal_id != self.proposal_id or from_uid in self.promises_rcvd:
            return None

        self.promises_rcvd.add( from_uid )
        
        if prev_accepted_id > self.last_accepted_id:
            self.last_accepted_id = prev_accepted_id
            # If the Acceptor has already accepted a value, we MUST set our proposal
            # to that value.
            if prev_accepted_value is not None:
                self.proposed_value = prev_accepted_value

        if len(self.promises_rcvd) > self.quorum_size/2:    
            if self.proposed_value is not None:
                self.amulti.accept(self.id, self.proposal_id, self.proposed_value)
                
class Acceptor (object):
    _sync = {}
    _async = ['set_multi', 'onPrepare', 'accept']
    _ref = ['set_multi', 'onPrepare']
    _parallel = []
    
    def __init__(self, quorum_size):
        self.accepted_id = None
        self.quorum_size = quorum_size
        self.accepted_value = None
        self.promised_id = None
        
    def set_multi(self, learners): 
        self.learners = learners
        self.amulti = AMulti(self.learners)
        
    def onPrepare(self, proposer, proposal_id):
        '''
        Called when a Prepare message is received from a Proposer
        '''
        if proposal_id == self.promised_id:
            # Duplicate prepare message
            proposer.promise(self.id, proposal_id, self.accepted_id, self.accepted_value)
        
        elif proposal_id > self.promised_id:
            self.promised_id = proposal_id
            proposer.promise(self.id, proposal_id, self.accepted_id, self.accepted_value)
        
                    
    def accept(self, from_uid, proposal_id, value):
        '''
        Called when an Accept! message is received from a Proposer
        '''
        if proposal_id >= self.promised_id:
            self.promised_id     = proposal_id
            self.accepted_id     = proposal_id
            self.accepted_value  = value
            '''send accepted to all learners!! '''
            self.amulti.accepted(self.id, proposal_id, self.accepted_value)
        
class Learner (object):
    _sync = {}
    _async = ['accepted']
    _ref = []
    _parallel = []
    proposals         = None # maps proposal_id => [accept_count, retain_count, value]
    acceptors         = None # maps from_uid => last_accepted_proposal_id
    final_value       = None
    final_proposal_id = None

    def __init__(self, quorum_size):
        self.quorum_size = quorum_size
    @property
    def complete(self):
        return self.final_proposal_id is not None


    def accepted(self, from_uid, proposal_id, accepted_value):
        '''
        Called when an Accepted message is received from an acceptor
        '''
        if self.final_value is not None:
            return # already done

        if self.proposals is None:
            self.proposals = dict()
            self.acceptors = dict()
        
        last_pn = self.acceptors.get(from_uid)

        if not proposal_id > last_pn:
            return # Old message

        self.acceptors[ from_uid ] = proposal_id
        
        if last_pn is not None:
            oldp = self.proposals[ last_pn ]
            oldp[1] -= 1
            if oldp[1] == 0:
                del self.proposals[ last_pn ]

        if not proposal_id in self.proposals:
            self.proposals[ proposal_id ] = [0, 0, accepted_value]

        t = self.proposals[ proposal_id ]

        assert accepted_value == t[2], 'Value mismatch for single proposal!'
        
        t[0] += 1
        t[1] += 1
        if t[0] > self.quorum_size/2:
            self.final_value       = accepted_value
            self.final_proposal_id = proposal_id
            self.proposals         = None
            self.acceptors         = None
            
            print 'Resolution!!', proposal_id, accepted_value
            
            
   
            #self.messenger.on_resolution( proposal_id, accepted_value )
            

