from multiprocessing.managers import BaseManager
from itertools import groupby
import random
import sysv_ipc
import signal
import os
import sys


class MyManager(BaseManager): pass


#KEYS
key = 350
keymain=400


def handler(sig, frame):
    if sig == signal.SIGINT:
        mq.remove()
        sm.del_all_offers()
        sys.exit(0)
    if sig == signal.SIGUSR1:
        for pid in mains_i.keys():
            os.kill(pid, signal.SIGUSR2)
        print("La partie est finie")
    sys.exit(1)


def deck(n):
    deck = []
    transports = ["Chaussure", "Velo", "Train", "Voiture", "Avion"]
    identical = True

    # On crée 5 cartes parmis les n premiers moyens de transport, n le nombre de joueur
    for j in transports[:3]:
        for _ in range(5):
            deck.append(j)

    # On vérifie que  cartes identiques ne se suivent pas car elles pourraient alors être distribuées à un joueur
    while identical == True:
        random.shuffle(deck)

        # On ajoute  à l'item de la liste pour chaque itération sur le groupe créé par groupby
        count_cons_dup = [sum(1 for _ in group) for _, group in groupby(deck)]

        try:
            count_cons_dup.index(5)
            print("Cinq cartes identiques consécutives, on recommence")
        except ValueError:
            identical = False
    
    return deck




if __name__ == "__main__":

    try:
        MyManager.register('sm') #On appelle le remote du fichier manager
        m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
        m.connect()
        sm = m.sm() #sm equivaut a remote
    except:
        print("La mémoire partagée n'est pas disponible")
        sys.exit(1)

    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)


    n = int(input("Combien de joueurs voulez vous dans cette partie ? (3-5)\n"))
    while n > 4:
        n = int(input('Attention! Le nombre maximum de joueur est de 5!\nEntrez le nombre de joueurs :\n'))
    
    # Liste de toutes les cartes du jeu, mélangées
    deck_cards = deck(n) #toutes les cartes du jeu
    mains_i = {} #La main de tous les joueurs
    

    i = 0
    k = 0

    while i < n:

        # Réception du pid du nouveau joueur qui se connecte
        pid, _ = mq.receive(type=1)
        pid = int(pid.decode())
        print("Nouveau joueur connecte :", pid)

        # Liste de moyen de transports
        main = deck_cards[k:k + 5]
        # Ajout de la liste au dictionnaire avec comme key le pid du Player
        mains_i[pid] = main #Chaque joueur a sa propre main

        msg = f"Bienvenue user {pid} ! Vous etes connecter a la partie, veuillez patienter dans la salle d'attente..."
        msg = msg.encode()

        
        mq.send(msg, type=pid)    

        pid_serveur=str(os.getpid())
        pid_serveur=pid_serveur.encode()
        mq.send(pid_serveur, type=pid) #On envoie le PID du serveur pour que less clients peuvent envoyer un signal au client (sonner la cloche)

        i =i+1
        k =k+5  #Chaque joueur doit avoir 5 cartes qui sont tires du deck

    
    for pid, list in mains_i.items():
        main = (' '.join(list)).encode()
        mq.send(main, type=pid)

    
    
    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGINT, handler)
    signal.pause()
    
#Fermer les msgs queues
#Continuer la partie
#Faire dict de scores