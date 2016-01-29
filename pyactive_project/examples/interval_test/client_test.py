from pyactive.controller import init_host,launch, start_controller,sleep

def client_test():

   tcpconf = ('tcp',('127.0.0.1',4324))
   host = init_host(tcpconf)
   e1 = host.lookup('tcp://127.0.0.1:1234/actor2/Echo/1')


   e1.echo('hola amigo')

   e1.echo('adeu')

def main():
   start_controller('pyactive_thread')
   launch(client_test)

if __name__ == "__main__":
   main()
