"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import controller
from constants import PARAMS, RESULT
import inspect

class Ref(object):
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
    def __init__(self, aref, gref=None):
        self.ref = aref
        self.group = gref

    def get_aref(self):
        return self.ref
