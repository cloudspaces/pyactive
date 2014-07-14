"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import stomp
#from stomp import ConnectionListener
import time

#import json

class Server(object):
    def __init__(self,host='127.0.0.2',port=61613):
        self.conn = stomp.Connection()
        self.conn.start()
        self.conn.connect(wait=True)
        

    def subs(self, listener, topic, headers={}):
        self.conn.set_listener('', listener)
        self.conn.subscribe(destination=topic,ack='auto',headers=headers)

    def pub(self,msg, topic, headers={}):
        self.conn.send(msg, destination=topic,headers=headers)
        
    def close(self):
        self.conn.stop()
        try:
            self.conn.disconnect()
        except Exception:
            pass
