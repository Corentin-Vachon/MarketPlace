import os
import queue
import sysv_ipc
import threading
from threading import *
from queue import *
from multiprocessing import *
import time
import sys
import sysv_ipc
from multiprocessing.managers import BaseManager
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

keyMarket = 100
keyHome = 110
mqMarket = sysv_ipc.MessageQueue(keyMarket)
mqHome = sysv_ipc.MessageQueue(keyHome)

global consommation
global production
mutex = Lock();
global compteur
global argent

consommation = 1
production = 1
compteur = 110
argent = 10000

def achatMaison1():
    print("Lancement thread  ACHAT TO HOME")
    global compteur
    while True:
        time.sleep(1)
        if compteur <= 80:
            message,t = mqHome.receive(type=20)
            message = message.decode()
            energie = message[:message.find(":")]
            with mutex:
                compteur = compteur + int(energie)
            print("Nouveau compteur suite à achat to HOME: " + str(compteur))

def venteMaison1():
    print("Lancement thread VENTE TO HOME")
    global compteur
    while True:
        time.sleep(1)
        if compteur > 120 :
            quantite = 20
            message = (str(quantite) + ":" + str(os.getpid()))
            mqHome.send(message.encode(), type = 20)
            with mutex:
                compteur = compteur - quantite
            print("Nouveau compteur suite à vente to HOME: " + str(compteur))

def achatauMarche2():
    print("Lancement thread  ACHAT TO MARKET")
    while True:
        time.sleep(1)
        if compteur <= 80:
            need = 20
            if need > argent :
                print("Vous n'avez plus d'argent ")
                break
            else:
                message = (str(need) +":"+str(os.getpid()))
                message = message.encode()
                mqMarket.send(message, type = 1)

def venteauMarche2():
    print("Lancement thread  VENTE TO MARKET")
    global compteur
    while True:
        time.sleep(1)
        if compteur >= 120:
            msg = 20
            message = (str(msg)+":"+str(os.getpid())).encode()
            mqMarket.send(message, type = 2)
            with mutex:
                compteur = compteur - msg

def achatBoth():
    print("Lancement thread  ACHAT TO HOME")
    global compteur
    while True:
        time.sleep(1)
        if compteur <= 80:
            message,t = mqHome.receive(type=70)
            message = message.decode()
            energie1 = message[:message.find(":")]
            energie = energie1[energie1.find("/")+1:]
            timestamp = energie1[:energie1.find("/")]
            #print("Compteur d'energie = " + energie)
            #print("Temps à l'envoi = " + timestamp)
            #print("Temps à l'arrivée= " + str(time.time()))
            if float(timestamp) + 10 > (time.time() ):
                with mutex:
                    compteur = compteur + int(energie)
                print("Nouveau compteur suite à achat to HOME:" + str(compteur))
            else:
                mqHome.send(message.encode(),type = 70)
                message = (str(20) +":"+str(os.getpid()))
                message = message.encode()
                mqMarket.send(message, type = 1)



def venteBoth():
    print("Lancement thread vente BOTH")
    global compteur
    global argent
    while True:
        time.sleep(1)
        if compteur > 120 :
            quantite = 20
            message = (str(time.time())+ "/" +str(quantite) + ":" + str(os.getpid()))
            mqHome.send(message.encode(), type = 70)
            time.sleep(10)
            mb,tb = mqHome.receive(type = 70)
            mb = mb.decode()
            pid = int(mb[message.find(":")+1:])
            if pid == os.getpid():
                message = mb[mb.find("/")+1:]
                message = message.encode()


                mqMarket.send(message, type = 2)
                with mutex:
                    compteur = compteur - quantite
            else:
                mqHome.send(mb.encode(),type = 70)
                with mutex:
                    compteur = compteur - quantite

def cons(queue1, data_ready):
    print("Lancement thread CONSOMMATION")
    global compteur
    global argent
    while True:
        m10, t10 = mqMarket.receive(type =int(str(3) + str(os.getpid())))
        if t10 == int(str(3) + str(os.getpid())):
            m10 = m10.decode()
            if m10[0:2] == "ok":
            #    print("OK EST RECU DE MARKET: " + m10)
                argent = argent + int(m10[2:])
                print("BAISSE DU COMPTEUR D'ENERGIE SUITE A VENTE TO MARKET: " + str(compteur))
                print("PORTE MONNAIE  MIS A JOUR: ----> Argent: "+ str(argent))
            else:
                with mutex:
                    compteur = compteur + 20 # récupère la quantité supposée perdue si acquittement


def prod(queue2, data_ready):
    print("Lancement thread  PRODUCTION")
    global compteur
    global argent
    global production
    while True:

        message2, t2 = mqMarket.receive(type = int(str(4) + str(os.getpid())))
        if t2 == int(str(4) + str(os.getpid())):
            message2 = message2.decode()
            if message2[0:2] == "ok":
                #print("OK EST RECU DE MARKET: " + message2)
                with mutex:
                    compteur = compteur + int(message2[2:])
                argent = argent - int(message2[2:])
                print("AUGMENTATION DU COMPTEUR D'ENERGIE SUITE A ACHAT TO MARKET: " + str(compteur))
                print("PORTE MONNAIE MIS A JOUR: ----> Argent: "+ str(argent))
                # TODO implémenter l'achat -> augmentation compteur energie...

def update():
    global consommation
    global production
    global compteur
    #i = 0
    class QueueManager(BaseManager):
        pass
    # QueueManager.register('get_queue')
    m = QueueManager(address=('', 50000), authkey=b'cupteam')
    m.connect()
    while True:
        #i += 1
        time.sleep(2)
        coefficient = m.get_queue()
        print(coefficient)
        coefficient = str(coefficient)
        coefficient = coefficient[13:len(coefficient)-2]
        coefficient = coefficient.split(',')
        coefficient = float(coefficient[0])+float(coefficient[1])+float(coefficient[2])+float(coefficient[3])
        coefficient = coefficient/200
        # TODO problème sur gestion du coefficient : utilisation d'un remplacement random
        coefficient = random.uniform(0.8,1.2)
        consommation = consommation * (1/coefficient)
        production = production * coefficient
        compteur = int(compteur*coefficient)
        print(compteur * coefficient, " compteur ")
        print("Votre compteur d'énergie est de: ---> " + str(int(compteur)))

        """if i % 150 < 50:
            with mutex:
                compteur = compteur * coefficient
        else:
            with mutex:
                compteur = compteur * (1/coefficient)"""

def creationHome(politique):
    print("Création du nouvel home entrant (process CREATIONHOME)")
    global consommation
    queue1 = queue.Queue()
    queue2 = Queue()
    data_ready = threading.Event()

    if politique == 1: # POLITIQUE ALWAYS GIVE AWAY
        entities = [
            Thread(target=cons, args=(queue1, data_ready)),
            Thread(target=prod, args=(queue2, data_ready)),
            Thread(target=achatMaison1),
            Thread(target=venteMaison1),
            Thread(target=update),
            ]
    elif politique == 2: # POLITIQUE ALWAYS SELL ON THE MARKET
        entities = [
            Thread(target=cons, args=(queue1, data_ready)),
            Thread(target=prod, args=(queue2, data_ready)),
            Thread(target=venteauMarche2),
            Thread(target=achatauMarche2),
            Thread(target=update),
            ]
    else: # SELL IF NO TAKERS
        entities = [
            Thread(target=cons, args=(queue1, data_ready)),
            Thread(target=prod, args=(queue2, data_ready)),
            Thread(target=achatBoth),
            Thread(target=venteBoth),
            Thread(target=update),
            ]

    for p in entities:
        p.start()

        # SI CHANGEMENT METEO OU EVENEMENT EXTERNE:
        # //TODO => Récuperer coefficient envoyé par weather ou external
#        queue1.put(value)
#        data_ready.set()

    for p in entities:
        p.join()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print ("Veuillez rentrer le type de politique en argument: 1, 2 ou 3")
        exit(1)
    politique = sys.argv[1]
    politique = int (politique)
    if politique != 1 and politique != 2 and politique != 3 :
        print("Erreur dans la saisie de l'argument concernant la politique")
        exit(1)

    # if len(sys.argv) > 1:
    #     name = sys.argv[2]
    #     mqMarket.send(name.encode(), type =100)

    p = Process(target=creationHome, args=(politique,))
    p.start()
    p.join()
