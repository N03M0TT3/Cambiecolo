from multiprocessing.managers import BaseManager
from itertools import groupby
import random
import time
import sysv_ipc
import signal
import os
import sys
import threading

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
        print("\nLa partie est terminée")
        # On supprime la message queue et on réinitialise la mémoire partagée
        for pid in cards_all.keys():
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                print("Un joueur est mort")

        mq.remove()

        sm.del_all_offers()
        sm.set_winner(-1)

        sys.exit(1)

    # L'un des joueurs a gagné
    if sig == signal.SIGUSR1:
        print("La partie est finie ! Le joueur", sm.get_winner() , "a gagné !")

        for pid in cards_all.keys():
            os.kill(pid, signal.SIGUSR2)
          
        sm.del_all_offers()
          

# Rejette les joueurs supplémentaires
def full():
    while True:
        try:
            pid, _ = mq.receive(type=1)
            pid = int(pid.decode())

            message = "La partie est pleine"
            mq.send(message.encode(), type=pid)
            time.sleep(5)
            break
        except sysv_ipc.ExistentialError:
            print("Partie terminée")
            break



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

    random.shuffle(deck_cards)
    k = 0
    for pid in cards_all.keys():
        # On stocke 5 cartes dans la variable cards
        cards = deck_cards[k:k + 5]
        # Ajout de la liste de cartes au dictionnaire avec comme key le pid du Player
        cards_all[pid] = cards
        k += 5


    # On envoie les cartes des joueurs à l'aide de la message queue
    for pid, l in cards_all.items():
        cards = (' '.join(l)).encode()
        mq.send(cards, type=pid)

    signal.pause()



if __name__ == "__main__":

    # Connection au remote manager
    try:
        MyManager.register('sm') # On appelle le remote du fichier manager
        m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
        m.connect()
        sm = m.sm() # sm équivaut a remote
        # Dans le cas d'une fermeture étrange du programme
        sm.set_winner(-1) 
        sm.del_all_offers()
    except:
        print("La mémoire partagée n'est pas disponible")
        sys.exit(1)

    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGUSR1, handler)

    thread = threading.Thread(target=full)

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
    
    
    thread.start()
    
    game() # Lancement de la partie
    
    while True: # Relancer des parties
        put = input("Voulez-vous relancer une partie ? (O/n) ")
        if put.capitalize() == 'O' or put == '':
            # Le gagnant ne sera pas le même + boucle Player.py
            sm.set_winner(-1)

            try:
                # On envoit un signal qui va relancer les processus Player.py
                for pid in cards_all.keys():
                    os.kill(pid, signal.SIGUSR1) # Signal "ON REJOUE"
            except:
                print("L'un des joueurs est mort")
                sys.exit(2)

            game()

        elif put.lower() == 'n':
            sm.set_winner(-1)
            print("Fin du jeu !")
            print("Le gagnant final est le joueur", sm.get_total_winner()[0], "avec", sm.get_total_winner()[1], "points !\n-----" )
            for joueur, score in sm.get_points().items():
                print(f"--> Joueur {joueur} a obtenu {score} points !")

            try:
                # On envoit un signal qui va tuer les processus Player.py
                for pid in cards_all.keys():
                    os.kill(pid, signal.SIGTERM)
            except:
                print("L'un des joueurs est mort")
                sys.exit(2)
            
            sm.del_all_points()
            mq.remove()
            sys.exit(1)
        else:
            print("Saisie non valide")