"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from threading import Thread, Timer, Event, currentThread
import time as timep

def later(timeout,f,*args, **kwargs):
    t = Timer(timeout, f, args)
    t.start()

def interval(time, f, *args, **kwargs):
    def wrap(*args, **kwargs):
        args = list(args)
        stop_event = args[0]
        del args[0]
        args = tuple(args)
        while not stop_event.is_set():
            stop_event.wait(time)
            f(*args, **kwargs)
    t2_stop = Event()
    args = list(args)
    args.insert(0, t2_stop)
    args = tuple(args)
    t = Thread(target=wrap, args=args, kwargs=kwargs)
    t.start()
    return t2_stop

def interval_host(host, time, f, *args, **kwargs):
    def wrap(*args, **kwargs):
        print args
        thread = currentThread()
        thread.get_ident()
        args = list(args)
        stop_event = args[0]
        del args[0]
        args = tuple(args)
        while not stop_event.is_set():
            stop_event.wait(time)
            f(*args, **kwargs)
        host.detach_interval(thread_id)
    print host, time
    t2_stop = Event()
    args = list(args)
    args.insert(0, t2_stop)
    args = tuple(args)
    t = Thread(target=wrap, args=args, kwargs=kwargs)
    t.start()
    thread_id = t.get_ident()
    host.attach_interval(thread_id, t2_stop)
    return t2_stop

def sleep(time):
    timep.sleep(time)
