from multiprocessing.managers import BaseManager
import random
import sysv_ipc
import signal
import os
import sys


class MyManager(BaseManager): pass


key = 300
#keymain=400
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)


def handler(sig, frame):
    if sig == signal.SIGUSR1:
        for pid in mains_i.keys():
            os.kill(pid, signal.SIGUSR2)
    print("La partie est finie")
    sys.exit(1)


def deck(n):
    deck = []
    transports = ["Chaussure", "Velo", "Train", "Voiture", "Avion"]
    for j in transports[:n]:
        for i in range(5):
            deck.append(j)
    random.shuffle(deck)
    return deck


if __name__ == "__main__":
    MyManager.register('sm') #On appelle le remote du fichier manager
    m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
    m.connect()
    sm = m.sm() #sm equivaut a remote
    n = int(input("Combien de joueurs voulez vous dans cette partie ? "))
    deck = deck(n) #toutes les cartes du jeu
    mains_i = {} #La main de tous les joueurs
    i = 0
    k = 0
    while i < n:
        pid, _ = mq.receive(type=1)
        pid = int(pid.decode())

        #Creation de le dictionnaire des offres et de la disponibilite de nos joueur
        offres = sm.get_offers()
        offres[pid] = []
        sm.set_offers(offres) # sauvegarder les modifs dans le basemanager

        dispo = sm.get_flag()
        dispo[pid] = True #indique que le joueur est disponible
        sm.set_flag(dispo)

        main = deck[k:k + 5]
        mains_i[pid] = main #Chaque joueur a sa propre main
        msg = "Bienvenu! Vous etes connecter a la partie, veuillez patienter dans la salle d'attente..."
        msg = msg.encode()
        
        mq.send(msg, type=pid)
        pid_serveur=str(os.getpid())
        pid_serveur=pid_serveur.encode()
        mq.send(pid_serveur) #On envoie le PID du serveur pour que less clients peuvent envoyer un signal au client (sonner la cloche)

        i =i+1
        k =k+5  #Chaque joueur doit avoir 5 cartes qui sont tires du deck
    #Creation nouvelle mq?
    #mq2=sysv_ipc.MessageQueue(keymain, sysv_ipc.IPC_CREAT)
    for pid, list in mains_i.items():
        main = (' '.join(list)).encode()
        mq.send(main, type=pid)
    #mq2.close()
    signal.signal(signal.SIGUSR1, handler)
    signal.pause()
#Fermer les msgs queues
#Continuer la partie
#Faire dict de scores