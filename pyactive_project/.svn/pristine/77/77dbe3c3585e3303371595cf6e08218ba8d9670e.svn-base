"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import stackless
import time
import tasklet

sleepingTasklets = []

def sleep(secondsToWait):
    channel = stackless.channel()
    endTime = time.time() + secondsToWait
    sleepingTasklets.append((endTime, channel))
    sleepingTasklets.sort()
    # Block until we get sent an awakening notification.
    channel.receive()

def ManageSleepingTasklets():
    while 1:
        if len(sleepingTasklets):
            endTime = sleepingTasklets[0][0]
            if endTime <= time.time():
                channel = sleepingTasklets[0][1]
                del sleepingTasklets[0]
                # We have to send something, but it doesn't matter what as it is not used.
                channel.send(None)
        stackless.schedule()

stackless.tasklet(ManageSleepingTasklets)()

def later(time, f, *args, **kwargs):
    """creates a tasklet that runs a function 'f' after time has passed
    """
    def wrap(*args, **kwargs):
        sleep(time)

        return f(*args, **kwargs)
        
    stackless.tasklet(wrap)(*args, **kwargs)


def interval(time, f, *args, **kwargs):
    """creates a tasklet that runs a function 'f' every time interval
    """
    
    def wrap(*args, **kwargs):
        while True:
            sleep(time)

            f(*args, **kwargs)
               
    t = stackless.tasklet(wrap)(*args, **kwargs)
#    tasklet.tasklets[t] = 'atom://localhost/'+f.__module__+'/'+f.__name__ 