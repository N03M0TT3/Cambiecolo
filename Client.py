import sysv_ipc
import os
import sys
import signal

def bell(pid):
    bell.acquire_bell()
    if main.count(main[0]) == len(main):
        os.kill(ppid,signal.SIGUSR1)
        print("Vous avez gagner")
    bell.release_bell()

def handler(sig,frame):
    if sig==signal.SIGUSR2:
        sys.exit(1)
key = 300
#keymain=400
# Creation of our message queue
try:
    mq = sysv_ipc.MessageQueue(key)
    #mq2= sysv_ipc.MessageQueue(keymain)
except sysv_ipc.ExistentialError:
    print("La message queue que vous essayez de rejoindre n'existe pas.")
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGUSR2,handler)
    pid = os.getpid()
    while True:
        connection = str(input("Voulez vous jouer ? (oui/non)"))
        if connection.lower() == "oui":
            print("Connection en cour...")
            break
        elif connection.lower() == "non":
            print("Au revoir.")
            sys.exit(1)
        #self.winner ou dans le dic offre?
        else:
            print("Saisie incorrecte veuillez reessayer")
    m = (str(pid)).encode()
    mq.send(m, type=1)
    
    m, _ = mq.receive(type=pid)
    m = m.decode()
    print(m) #Vous etes connecte
    #pid du serveur
    m, _ = mq.receive(type=pid)
    ppid = int(m.decode())
    #Obtention de la main du client
    m, _ = mq.receive(type=pid) #2
    main=(m.decode()).split()