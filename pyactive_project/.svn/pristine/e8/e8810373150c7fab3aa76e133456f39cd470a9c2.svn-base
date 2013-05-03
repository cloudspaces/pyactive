"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from threading import Thread, Timer
import time as timep

def later(timeout,f,*args, **kwargs):
    t = Timer(timeout, f, args)
    t.start()

def interval(time, f, *args, **kwargs):
    
    def wrap(*args, **kwargs):
        while True:
            timep.sleep(time)

            f(*args, **kwargs)
    
    t = Thread(target=wrap, args=args, kwargs=kwargs)         
    t.start()
    
def sleep(time):
    timep.sleep(time)