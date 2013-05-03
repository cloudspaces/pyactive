"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host,launch, start_controller

def client_test():
    
    tcpconf = ('tcp',('127.0.0.1',4321))
    host = init_host(tcpconf)
    server = host.lookup('tcp://127.0.0.1:1234/server/Registry/1')
    server.hello()
    print server.hello_sync()
    host.shutdown()
def main():
    start_controller('tasklet')
    launch(client_test)

if __name__ == "__main__":
    main()