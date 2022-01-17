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
    
    valid = input("Est-ce que vous validez ? (O/n)")
    if valid == 'O' or valid == '':
        print("C'est validé")
        sm.add_offer(pid, cards)
    else:
        print("Offre annulée")


def accept_offer(offers, pid, cards):
    see_all_offers(offers)
    offre = int(input("\nEntrez le numéro de l'offre que vous souhaitez accepter : "))
    print("Il faut que vous échangiez", len(offers.get(list(offers.keys())[offre - 1])) , "cartes. Lesquels ?")
    choose_cards(cards)



def see_all_offers(offers):
    print("\nOFFRES :")
    i = 0
    for player in offers.keys():
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
        
        try:
            msg, t = mq.receive(block=False, type=pid+10)
        except sysv_ipc.BusyError:
            pass
        finally:
            print("\nYou have no offers")

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
            choose_cards(cards)
        elif put == 'A':
            accept_offer(sm.get_offers(), pid, cards)
        elif put == 'V':
            pass
        else:
            print("Cette action n'est pas disponible")

        


            



