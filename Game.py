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

# Création de la message queue
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

cards_all = {} # Les cartes de tous les joueurs



# Handles signals
def handler(sig, frame):
    # Interruption du programme par Ctrl+C
    if sig == signal.SIGINT:
        # On supprime la message queue et on réinitialise la mémoire partagée
        mq.remove()

        sm.acquire_lock()
        sm.del_all_offers()
        sm.set_winner(-1)
        sm.release_lock()

        sys.exit(0)

    # L'un des joueurs a gagné
    if sig == signal.SIGUSR1:
        print("La partie est finie ! Le joueur", sm.get_winner() , "a gagné !")

        # On supprime la message queue et on réinitialise la mémoire partagée
        mq.remove()
        sm.acquire_lock()
        sm.del_all_offers()
        sm.del_all_points()
        sm.set_winner(-1)
        sm.release_lock()

        while True:
            put = input("Voulez-vous relancer une partie ? (O/n) ")
            if put.capitalize() == 'O' or put == '':
                game()
                break
            elif put.lower() == 'n':
                print("Fin du jeu !")
                print("Le gagnant final est le joueur", sm.get_total_winner()[0], "avec", sm.get_total_winner()[1], "points !" )

                # On envoit un signal qui va tuer les processus Player.py
                for pid in cards_all.keys():
                    os.kill(pid, signal.SIGINT)

                sys.exit(1)
            else:
                print("Saisie non valide")




# Cette fonction crée les cartes du jeux et vérifie que 5 cartes identiques ne se suivent pas
def deck(n):
    deck = []
    transports = ["Chaussure", "Velo", "Train", "Voiture", "Avion"]

    # Flag
    identical = True

    # On crée 5 cartes parmis les n premiers moyens de transport, n le nombre de joueur
    for j in transports[:n]:
        for _ in range(5):
            deck.append(j)

    # On vérifie que cartes identiques ne se suivent pas car elles pourraient alors toutes être distribuées au même joueur
    while identical == True:
        random.shuffle(deck)

        # On ajoute  à l'item de la liste pour chaque itération sur le groupe créé par groupby
        count_cons_dup = [sum(1 for _ in group) for _, group in groupby(deck)]

        try:
            # On essaye de trouver un groupe de 5
            count_cons_dup.index(5)
            print("Cinq cartes identiques consécutives, on recommence")
        except ValueError:
            identical = False
    
    return deck


def game():
    n = input("Combien de joueurs voulez vous dans cette partie ? (3-5)\n")

    # Flag
    valid = False
    while not valid:
        try:
            n = int(n)
            while not (3 <= n <= 5):
                n = int(input("Entrez un entier entre 3 et 5 : "))
            # Ici n est un entier entre 3 et 5, on peut sortir de la boucle
            valid = True
        except ValueError:
            n = input("Entrez un entier entre 3 et 5 : ")
    
    
    
    # Liste de toutes les cartes du jeu, mélangées
    deck_cards = deck(n) 
    
    
    # i = joueur
    i = 0
    # k = cartes
    k = 0

    while i < n:

        # Réception du pid du nouveau joueur qui se connecte
        pid, _ = mq.receive(type=1)

        try:
            pid = int(pid.decode())
        except ValueError:
            break
        
        print("Nouveau joueur connecte :", pid)

        # On stocke 5 cartes dans la variable cards
        cards = deck_cards[k:k + 5]
        # Ajout de la liste de cartes au dictionnaire avec comme key le pid du Player
        cards_all[pid] = cards 

        msg = f"Bienvenue user {pid} ! Vous etes connecter a la partie, veuillez patienter dans la salle d'attente..."
        msg = msg.encode()

        mq.send(msg, type=pid)    

        # On cherche à transmettre le pid du processus Game pour permettre la fin du jeu
        pid_serveur = str(os.getpid())
        pid_serveur = pid_serveur.encode()
        mq.send(pid_serveur, type=pid) 

        i = i + 1
        k = k + 5  # Chaque joueur doit avoir 5 cartes qui sont tirées du deck

    # On envoie les cartes des joueurs à l'aide de la message queue
    for pid, l in cards_all.items():
        cards = (' '.join(l)).encode()
        mq.send(cards, type=pid)



if __name__ == "__main__":

    # Connection au remote manager
    try:
        MyManager.register('sm') # On appelle le remote du fichier manager
        m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
        m.connect()
        sm = m.sm() # sm équivaut a remote
        sm.set_winner(-1) # Dans le cas d'une fermeture étrange du programme
    except:
        print("La mémoire partagée n'est pas disponible")
        sys.exit(1)


    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGUSR1, handler)
    
    
    game()
    
    
    
    