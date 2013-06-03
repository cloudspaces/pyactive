"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

class PyactiveError(Exception):
    def __init__(self, e=None):
        self.e = e
    
    def __str__(self):
        return self.e.__str__()


class TimeoutError(PyactiveError):
    def __str__(self):
        return 'The timeout has expired'
    
class NotFoundDispatcher(PyactiveError):
    def __str__(self):
        return 'Not found dispatcher, it is possible this dispatcher not work with this actor'

class NotExistsMethod(PyactiveError):
    def __str__(self):
        return 'This method not exists'
    
class MethodNotFoundError(PyactiveError):
    def __str__(self):
        return 'The method was not found'
    
class MethodError(PyactiveError):
    def __str__(self):
        return 'Incorrect parameters'

class NotImplementedMethod(PyactiveError):
    def __str__(self):
        return 'Please implement this method'