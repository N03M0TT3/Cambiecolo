from multiprocessing.managers import BaseManager
import sysv_ipc
import os
import sys
import signal


class MyManager(BaseManager): pass


# KEYS
key = 350
keymain=400


def bell(pid):
    sm.bell.acquire_bell()
    if cards.count(cards[0]) == 5 :
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
            

def choose_cards(current_cards):
    # Display cards
    i = 0
    for card in current_cards:
        i += 1
        print(i, " -> ", card)

    # User input
    put = input("Entrez les numéros des cartes à échanger séparés par un point virgule (;) :\n")

    cards = []

    for num in put.split(';'):
        print("La carte", int(num), "(", current_cards[int(num)-1], ") a été sélectionnée")
        cards.append(current_cards[int(num)-1])
    
    put = input("Est-ce que vous validez ? (O/n) ")
    if put == '' or put == 'O' :
        valid = True
    else :
        valid = False

    return valid, cards
    

def accept_offer(offers, pid, cards):
    # Affichage des offres disponible, numérotées de 1 à n max
    see_all_offers(offers)

    offre = int(input("\nEntrez le numéro de l'offre que vous souhaitez accepter : "))
    pid_offre = list(offers.keys())[offre - 1]
    nb_cards = len(offers.get(pid_offre))

    print("Il faut que vous échangiez", nb_cards , "cartes. Lesquels ?")

    res = choose_cards(cards)

    if len(res[1]) != nb_cards:
        print("\nVous avez sélectionné un nombre incorrect de cartes !\nRecommencez en sélectionant", nb_cards, "cartes :")
        res = choose_cards(cards)

    if res[0]:  # La sélection du Player est validée
        sm.add_offer(-pid_offre, res[1])
        print("\nLes cartes", res[1], "ont été envoyées")

        new_cards = offers.get(pid_offre)
        print("Les cartes", new_cards, " ont été réceptionnées\n")

        for i in range(nb_cards):
            cards.pop(cards.index(res[1][i]))
            cards.append(new_cards[i])

        print("Vos cartes sont maintenant :")
        print_deck(pid, cards)
    else:
        p = input("Voulez-vous sortir de l'acceptation d'offre ? (O/n) ")
        if p == 'n':
            accept_offer(offers, pid, cards)



def see_all_offers(offers):
    print("\nOFFRES :")
    i = 0
    for player in offers.keys():
        if player >= 0:  # Will not print responses to offers
            i += 1
            print(i, "--> Player", player, "propose", len(offers.get(player)), "cartes")
            print("---------")


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
        connection = str(input("Voulez vous jouer ? (oui/non) "))
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
    cards = (m.decode()).split()
    print_deck(pid, cards)



    while sm.getwinner() == -1:
        
        # try:
        #     msg, t = mq.receive(block=False, type=pid+10)
        # except sysv_ipc.BusyError:
        #     pass
        # finally:
        #     print("\nYou have no offers")

        if sm.get_offers().get(-pid) != None:
            sent = sm.get_offers().get(pid)
            received = sm.get_offers().get(-pid)

            for i in range(len(sent)):
                cards.pop(cards.index(sent[i]))
                cards.append(received[i])

            sm.del_offer(pid)
            sm.del_offer(-pid)

            print("Transaction terminée, voici vos cartes :")
            print_deck(pid, cards)

        print("******************")
        put = input("""Que voulez-vous faire ?\n
        Afficher vos cartes (C)
        Afficher les offres (O)
        Proposer une offre (P)
        Accepter une offre (A)
        Vérifier vos offres (V)\n""")

        if put == 'C':
            print_deck(pid, cards)

        elif put == 'O':
            see_all_offers(sm.get_offers())

        elif put == 'P':
            print("\nChoose cards to offer :")
            # Returne un boolean True si le Player confirme son choix, et les cartes sélectionnées
            res = choose_cards(cards)  
            if res[0] :
                print("C'est validé")
                sm.add_offer(pid, res[1])
            else:
                print("Offre annulée")
            
        elif put == 'A':
            accept_offer(sm.get_offers(), pid, cards)

        elif put == 'V':
            pass

        else:
            print("Cette action n'est pas disponible")

        


            



