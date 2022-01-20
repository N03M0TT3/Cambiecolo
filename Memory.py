from multiprocessing.managers import BaseManager
from multiprocessing import Lock


class MyRemoteClass: #Gestion memoire partagee

    def __init__(self):
        self.disponible = {}
        self.offres = {}
        self.lock = Lock()
        self.winner = -1

    def get_disp(self):
        return self.disponible()

    def set_disp(self,bool, key):
        self.disponible[key]=bool

    def get_offers(self):
        return self.offres


    def add_offer(self, pid, cards):
        self.offres[pid] = cards


    def del_offer(self, pid):
        self.offres.pop(pid, None)


    def del_all_offers(self):
        self.offres.clear()


    def acquire_lock(self):
        self.lock.acquire()


    def release_lock(self):
        self.lock.release()


    def get_winner(self):
        return self.winner


    def set_winner(self, pid):
        self.winner = pid
    


class MyManager(BaseManager): #MyManager is a BaseManager
    pass


remote = MyRemoteClass() #Objet de la classe de gestion de memoire

MyManager.register('sm', callable=lambda: remote) #lie le remote au MyManager (du coup au BaseManager)
m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra') #Point d'acces au Manager
s = m.get_server() #Active le manager

print("La mémoire partagée est activée")

s.serve_forever()