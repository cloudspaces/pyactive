"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller, interval, sleep
#from loguml import write_uml
from pyactive.Multi import AMulti, SMulti
ABORT = -1
COMMIT = 1

class Coordinator():
    _sync = {'commit': '1', 'set_cohorts': '2'}
    _async = ['hello_world']
    _ref = []
    _parallel = []


    def __init__(self):
        self.cohort = None
        self.abort = False
        print 'hola que tal! init'


    def set_cohorts(self,cohortlist):
        self.amulti = AMulti(cohortlist)
        print 'self.amulti', self.amulti
        self.smulti = SMulti(self._atom, cohortlist)
        print 'self.smulti', self.smulti
        return True

    def commit(self):
        vote = COMMIT
        votes = self.smulti.vote_request()
        #print votes
        if votes.__contains__(ABORT):
            self.abort = True
        self.final_decision()
        print 'hola que tal!'
        return True

    def final_decision(self):
        if self.abort==True:
            self.amulti.global_abort()
        else:
            self.amulti.global_commit()





class GoodCohort():
    _sync = {'vote_request': '1'}
    _async = ['global_commit', 'global_abort']
    _ref = []
    _parallel = []
    def __init__(self,coordinator=None):
        self.coordinator = coordinator
        print 'hola que tal!'

    #@msync(1)
    def vote_request(self):
        print 'receiving vote request...'
        return COMMIT
    #@masync
    def global_commit(self):
        print 'global commit',self.id
    #@masync
    def global_abort(self):
        print 'global abort',self.id

#@group(2pc)
class BadCohort():

    _sync = {'vote_request': '1'}
    _async = ['global_commit', 'global_abort']
    _ref = []
    _parallel = []
    def __init__(self,coordinator=None):
        self.coordinator = coordinator

    #@msync(1)
    def vote_request(self):
        print 'receiving vote request...'
        return ABORT
    #@masync
    def global_commit(self):
        print 'global commit',self.id
    #@masync
    def global_abort(self):
        print 'global abort',self.id




def test_2pc():
    host = init_host()
    #log = host.spawn('loguml','LogUML',[])
    #host.set_tracer(log)
    coord = host.spawn_id('5', '2pc_multi','Coordinator',[])

    cohort1 = host.spawn_id('1', '2pc_multi','GoodCohort',[coord])
    cohort2 = host.spawn_id('2', '2pc_multi','GoodCohort',[coord])
    cohort3 = host.spawn_id('3', '2pc_multi','GoodCohort',[coord])
    cohort4 = host.spawn_id('4', '2pc_multi','GoodCohort',[coord])

    coord.set_cohorts([cohort1, cohort2, cohort3, cohort4])

    coord.commit()
    print 'hola que tal!'
    sleep(1)
    #write_uml('2pc.sdx',log.to_uml())



def test_2pc_bad():
    host = init_host()
    coord = host.spawn_id('5','2pc_multi','Coordinator',[])

    cohort1 = host.spawn_id('1','2pc_multi','GoodCohort',[coord])
    cohort2 = host.spawn_id('2','2pc_multi','BadCohort',[coord])
    cohort3 = host.spawn_id('3','2pc_multi','GoodCohort',[coord])
    cohort4 = host.spawn_id('4','2pc_multi','BadCohort',[coord])

    coord.set_cohorts([cohort1, cohort2, cohort3, cohort4])

    coord.commit()

    sleep(1)



def main():
    start_controller('pyactive_thread')
    launch(test_2pc)
    print 'now testing bad...'
    launch(test_2pc_bad)
    #test1()

if __name__ == "__main__":
    main()
