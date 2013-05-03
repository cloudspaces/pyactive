"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import controller
from constants import PARAMS, RESULT
import inspect

class Ref():
    pass
    
def ref_l(f):
    def wrap_ref_l(*args):
        args[0][PARAMS] = controller.get_host()._loads(args[0][PARAMS])
        return f(*args)
    return wrap_ref_l

def ref_d(f):
    def wrap_ref_d(*args):
        args[1][RESULT] = controller.get_host()._dumps(args[1][RESULT])
        return f(*args)
    return wrap_ref_d

class AtomRef(Ref):
    def __init__(self, aref):
        self.ref = aref
    
    def get_aref(self):
        return self.ref
    
def methodsWithDecorator(cls, decoratorName):
    """Scan code to find the methods that need some decorator"""
    sourcelines = inspect.getsourcelines(cls)[0]
    for i, line in enumerate(sourcelines):
        line = line.strip()
        if line.split('(')[0].strip() == '#@' + decoratorName:  # leaving a bit out
            nextLine = sourcelines[i + 1]
            if nextLine.strip().find('def') == 0:
                name = nextLine.split('def')[1].split('(')[0].strip()
                yield(name)
            else:
                nextLine2 = sourcelines[i + 2]
                name = nextLine2.split('def')[1].split('(')[0].strip()
                yield(name)
                


def methodsWithSync(cls):
    """Special method to scan methods with sync decorator, because need timeOut also"""
    sourcelines = inspect.getsourcelines(cls)[0]
    dict = {}
    for i, line in enumerate(sourcelines):
        line = line.strip()
        if line.split('(')[0].strip() == '#@sync':
            nextLine = sourcelines[i+1]
            if nextLine.strip().find('def') == 0:
                timeout = line.split('(')[1].strip(')')
                name = nextLine.split('def')[1].split('(')[0].strip()
                dict[name] = timeout
    return dict
