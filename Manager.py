from multiprocessing.managers import BaseManager
from multiprocessing import Lock


class MyRemoteClass: #Gestion memoire partagee

    def __init__(self):
        self.disponible = {}
        self.offres = {}
        self.lock = Lock()
        self.bell=Lock()
        #self.winner ou dans le dic offre?
        self.winner=-1

    def get_flag(self):
        return self.disponible

    def set_flag(self, pushed_bool, key):
        self.disponible[key] = pushed_bool

    def get_offers(self):
        return self.offres

    def set_offers(self, offres):
        self.offres[offres.key] = offres.value

    def acquire_lock(self):
        self.lock.acquire()

    def acquire_bell(self):
        self.bell.acquire

    def release_lock(self):
        self.lock.release()

    def release_bell(self):
        self.bell.release()

    def getwinner(self):
        return self.winner
    
    def setwinner(self,pid):
        self.winner=pid
    
class MyManager(BaseManager): #My manager is a BaseManager
    pass


remote = MyRemoteClass() #Objet de la classe de gestion de memoire

MyManager.register('sm', callable=lambda: remote) #lie le remote au MyManager (du coup au BaseManager)
m = MyManager(address=("127.0.0.1", 8888), authkey=b'abracadabra') #Point d'acces au Manager
s = m.get_server() #Active le manager
s.serve_forever()