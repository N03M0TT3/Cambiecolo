from multiprocessing.managers import BaseManager
import sysv_ipc
import os
import sys
import signal


class MyManager(BaseManager): pass


def bell(pid):
    sm.bell.acquire_bell()
    if main.count(main[0]) == len(main):
        os.kill(ppid,signal.SIGUSR1)
        print("Vous avez gagner")
    sm.bell.release_bell()


def handler(sig,frame):
    if sig==signal.SIGUSR2:
        sys.exit(1)


def print_deck(pid, current_cards):
        print("Player n° :", pid)
        for card in current_cards:
            print("--> ", card)


def see_all_offers(offers):
    for player in offers.keys():
        print("Player", player, "proposes", len(offers.get(player)), "cards")
        print("---------")


key = 350
keymain=400

# Creation of our message queue
try:
    mq = sysv_ipc.MessageQueue(key)
except sysv_ipc.ExistentialError:
    print("La message queue que vous essayez de rejoindre n'existe pas.")
    sys.exit(1)


if __name__ == "__main__":

    signal.signal(signal.SIGUSR2,handler)
    
    MyManager.register('sm') #On appelle le remote du fichier manager
    m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
    m.connect()
    sm = m.sm() #sm equivaut a remote

    pid = os.getpid()
    
    while True:
        connection = str(input("Voulez vous jouer ? (oui/non)"))
        if connection.lower() == "oui" or connection == "":
            print("Connection en cours...")
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
    # print(ppid)

    #Obtention de la main du client
    m, _ = mq.receive(type=pid) #2
    main = (m.decode()).split()
    print_deck(pid, main)

    print(sm.get_offers())

    sm.add_offer(pid, ["Vélo", "Vélo"])

    print(sm.get_offers())

    sm.del_offer(pid)

    print(sm.get_offers())

    # while sm.getwinner() == -1:
        
    #     try:
    #         msg, t = mq.receive(10+pid)
    #     except sysv_ipc.BusyError:
    #         pass
    #     finally:
    #         print("ok")


            



