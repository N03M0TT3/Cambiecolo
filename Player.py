from multiprocessing.managers import BaseManager
import sysv_ipc
import os
import sys
import signal


class MyManager(BaseManager): pass


# KEYS
key = 350

# Vérification des conditions de victoire et envoie du signal au process Game.py
def bell(pid):
    sm.acquire_bell()  # Get Lock on bell

    if cards.count(cards[0]) == 5 : # Si la carte 0 est présente 5 fois dans les cartes du joueur, il a gagné
        # On écrit son pid dans la mémoire partagée
        sm.set_winner(pid)
        # On envoie le signal SUGUSR1 au processus Game.py
        os.kill(pid_game, signal.SIGUSR1)
        print("Vous avez gagné ! Félicitations !")

    sm.release_bell()  # Releases Lock on bell


# Handles signals
def handler(sig, frame):
    if sig == signal.SIGUSR2 and sm.get_winner() != None:
        print("Le joueur", sm.get_winner() , "a gagné !")
        sys.exit(1)


# Imprime la main courante du joueur
def print_deck(pid, current_cards):

        print("Player n° :", pid)

        for card in current_cards:
            print("--> ", card)
            

# Sélection de cartes à échanger : lors d'une proposition ou d'une acceptation
def choose_cards(current_cards):
    # Afficahe des cartes avec un compteur
    i = 0
    for card in current_cards:
        i += 1
        print(i, " -> ", card)

    # Flag input utilisateur
    valid = False

    while not valid:

        put = input("Entrez les numéros des cartes à échanger séparés par un point virgule (;) :\n")
        # On sépare l'input en une liste de string
        nums = put.split(';')

        # On part du principe que l'input est valide (seulement des entiers séparés par des ";")
        valid = True

        for num in nums:
            if len(num) != 1: # Un chiffre ne compte que comme un caractère
                print("\nLes numéros doivent être séparés par des virgules et sont compris entre 1 et 5")
                valid = False
            else:
                try:
                    n = int(num)

                    if n > 5:
                        print("\nVous n'avez que 5 cartes")
                        valid = False
                    # Ici tous les tests sont validés, valid est resté True donc on sort de la boucle
                except ValueError:
                    print("\nLes numéros sont des entiers entre 1 et 4")
                    valid = False

    print()

    cards = []
    # Tous les num sont des entiers entre 1 et 5 ici
    for num in nums:
        print("La carte", int(num), "(", current_cards[int(num)-1], ") a été sélectionnée")
        cards.append(current_cards[int(num)-1])
    
    while True:

        put = input("Est-ce que vous validez ? (O/n) ")

        if put == '' or put == 'O' :
            valid = True
            break
        elif put == 'n':
            valid = False
            break
        else:
            print("Saisie invalide")

    # On retourne un boolean et la liste des cartes sélectionnées
    return valid, cards
    

def accept_offer(offers, pid, cards):
    # On stocke temporairement les cartes de l'offre
    temp = sm.get_offers().get(pid)
    sm.del_offer(pid)

    # Affichage des offres disponible, numérotées de 1 à n max
    see_all_offers(offers, pid)

    # Flag
    valid = False
    while not valid:

        try:
            offre = int(input("\nEntrez le numéro de l'offre que vous souhaitez accepter : "))
            if offre < 1:
                print("Les numéros des offres commencent à 1")
            elif offre > len(offers):
                print("Ceci est trop grand")
            else:
                valid = True
        
        except ValueError:
            print("Merci d'entrer un chiffre")

    # Récupération de la clé de l'offre choisie par le Player
    pid_offre = list(offers.keys())[offre - 1]
    # Nombre de cartes proposées dans cette offre
    nb_cards = len(offers.get(pid_offre))

    print("Il faut que vous échangiez", nb_cards , "cartes. Lesquels ?")

    # On récupére les cartes choisies par le Player
    res = choose_cards(cards)

    # Flag
    nb_valid = False
    while not nb_valid:

        if len(res[1]) != nb_cards:
            print("\nVous avez sélectionné un nombre incorrect de cartes !\nRecommencez en sélectionant", nb_cards, "cartes : ")
            res = choose_cards(cards)
        else:
            nb_valid = True


    if res[0]:  # La sélection du Player est validée
        # On rajoute une offre avec comme clé la valeur opposée de la clé de l'offre acceptée et comme valeur les cartes choisies pour être échangées
        sm.add_offer(-pid_offre, res[1])
        print("\nLes cartes", res[1], "ont été envoyées")

        # On récupère de la mémoire les cartes de l'autre Player
        new_cards = offers.get(pid_offre)
        print("Les cartes", new_cards, " ont été réceptionnées\n")

        # On supprimer de la main du Player les cartes envoyées et on ajoute les nouvelles
        for i in range(nb_cards):
            cards.pop(cards.index(res[1][i]))
            cards.append(new_cards[i])

        print("Vos cartes sont maintenant :")
        # Le deck est imprimé au début de la boucle du jeu
    else:   # Le joueur n'a pas validé sa sélection

        while True:

            p = input("Voulez-vous sortir de l'acceptation d'offre ? (o/N) ")
            if p == 'N' or p == '':
                accept_offer(offers, pid, cards)
            elif p == 'o':
                # On réinstaure l'offre d'avant
                sm.add_offer(pid, temp)
                break
            else:
                print("Saisie invalide")


# Affichage de toutes les offres
def see_all_offers(offers, pid):
    print("\nOFFRES :")

    # Compteur pour l'UX
    i = 0
    for player in offers.keys():
        if player >= 0 and player != pid:  # N'affiche pas les réponses aux offres ni l'offre du Player
            i += 1
            print(i, "--> Player", player, "propose", len(offers.get(player)), "cartes")
            print("---------")


# MAIN
if __name__ == "__main__":

    # Connection à la message queue
    try:
        mq = sysv_ipc.MessageQueue(key)
    except sysv_ipc.ExistentialError:
        print("La message queue que vous essayez de rejoindre n'existe pas.")
        sys.exit(1)


    signal.signal(signal.SIGUSR2, handler)

    # Connection à la mémoire partagée
    MyManager.register('sm')
    m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra')
    m.connect()
    sm = m.sm() #sm equivaut a remote

    pid = os.getpid()
    
    while True:

        connection = input("Voulez vous jouer ? (O/n) ")

        if connection == "O" or connection == "":
            print("Connection en cours...")
            break
        elif connection == "n":
            print("Au revoir.")
            sys.exit(1)
        else:
            print("Saisie incorrecte veuillez reessayer")
    
    # Envoie du pid du joueur au processus Game.py
    m = (str(pid)).encode()
    mq.send(m, type=1)
    

    m, _ = mq.receive(type=pid)
    m = m.decode()
    print(m) # Message de de bonne connexion avec Game

    # Récupération du pid du serveur
    m, _ = mq.receive(type=pid)
    pid_game = int(m.decode())


    # Obtention de la main du client
    m, _ = mq.receive(type=pid) 
    cards = (m.decode()).split()

    print()
    print("DEBUT DU JEU")


    ########### BOUCLE DU JEU ###########

    while sm.get_winner() == -1:

        # Si le Player a vu son offre être acceptée
        if sm.get_offers().get(-pid) != None:
            
            #Récupération des cartes que le Player a envoyé et de celles qu'il a reçu
            sent = sm.get_offers().get(pid)
            received = sm.get_offers().get(-pid)

            # Echange des anciennes cartes avec les nouvelles
            for i in range(len(sent)):
                cards.pop(cards.index(sent[i]))
                cards.append(received[i])

            # On peut supprimer les deux offres maintenant que la transaction est terminée
            sm.del_offer(pid)
            sm.del_offer(-pid)

            print("Transaction terminée, voici vos cartes :")
            print_deck(pid, cards)

        else: # Pas d'offres acceptée, comportement "usuel"
            print_deck(pid, cards)

        # Gestion de l'input du Player
        print("******************")
        put = input("""Que voulez-vous faire ?\n
        Afficher vos cartes (C)
        Afficher les offres (O)
        Proposer une offre (P)
        Accepter une offre (A)
        Sonner la cloche (B)\n""")

        if put == 'C':
            pass # Les cartes sont affichées en début de la boucle du jeu

        elif put == 'O':
            see_all_offers(sm.get_offers(), pid) # On affiche toutes les offres de la mémoire
            print()

        elif put == 'P':
            print("\nChoisir les cartes à proposer :")
            # Returne un boolean True si le Player confirme son choix, et les cartes sélectionnées
            res = choose_cards(cards)  

            if res[0] :
                print("\n==> C'est validé\n")
                # On rajouter l'offre à la mémoire partagée
                sm.add_offer(pid, res[1])
            else:
                print("\n==> Offre annulée...\n")
            
        elif put == 'A':
            accept_offer(sm.get_offers(), pid, cards)

        elif put == 'B': 
            bell(pid) # Test des conditions de victoire

        else:
            print("Cette action n'est pas disponible")

        


            



