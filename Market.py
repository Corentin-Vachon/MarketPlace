import os
import random
import signal
import threading
import time
from multiprocessing import Process, Value
from threading import *
from queue import *
import sysv_ipc as sysv_ipc
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Partie variable globale ----------------------------------------------------

PRIX = 1000

# ventemq = sysv_ipc.MessageQueue(58, sysv_ipc.IPC_CREAT)
# achatmq = sysv_ipc.MessageQueue(44, sysv_ipc.IPC_CREAT)

marketQueue = sysv_ipc.MessageQueue(100, sysv_ipc.IPC_CREAT)
homeQueue = sysv_ipc.MessageQueue(110, sysv_ipc.IPC_CREAT)
mutex = Lock();
secondmutex = Lock();

# type 1 --> le marché achete de l'energie auprés d'une maison
# type 2 --> le marché vend de l'énergie
# type 3 --> envoie ACK de vente
# type 4 --> envoie de l'ACK d'achat du marché vers la maison
# type 11 --> check type1
# type 21 --> check type2
# type 3 --> confirme
# type 999 --> changement de prix external
# type 100 --> une nouvelle maison se connecte auprés du marché

# Partie achat ----------------------------------------------------

def achat():
    global ENERGY
    marketQueue = sysv_ipc.MessageQueue(100)

    while True:
        message, t = marketQueue.receive(type = 1)
        message = message.decode()

        pid = message[message.find(":")+1:]
        message = int(message[:message.find(":")])


        with mutex:
            ENERGY = ENERGY - message
            if ENERGY <= 0 :
                print("Le market n'a plus d'énergie, arrêt de la simulation")
                exit(1)
        print("L'achat s'est bien effectué, l'énergie était de ", ENERGY,
                " elle est maintenant de : ", ENERGY - message)
        price = ("a"+str(message)).encode()
        message2 = "ok" + str(message)
        marketQueue.send(message2.encode(), type=int( str('4')+ pid ))
        #print(int( str('4')+str(t)[1:]) , message2)
        marketQueue.send(price, type=999)

        # TODO remettre la demande de la maison dans la queue


# Partie vente ----------------------------------------------------

def vente():
    global ENERGY
    marketQueue = sysv_ipc.MessageQueue(100)

    while True:
        message, t = marketQueue.receive(type=2)

        if (t == 2):
            message = message.decode()
            pid = message[message.find(":")+1:]
            message = int(message[:message.find(":")])
            with mutex:
                ENERGY = ENERGY + message
            print("La vente s'est bien effectuée, l'énergie était de ", ENERGY,
                  " elle est maintenant de : ", ENERGY + message)
            price = ("v"+str(message)).encode()
            marketQueue.send(price, type=999)
            message3 = "ok" + str(message)
            marketQueue.send(message3.encode(), type=int( "3"+ pid ))


# Partie prix ----------------------------------------------------

def underprice(externalprice, data_ready):
    while True:
        pass


def price(externalprice, data_ready):
    global PRIX
    PRIX = 10

    pricechild = Thread(target=underprice)  # Lancement d'un thread fils TODO
    pricechild.start()

    global ENERGY
    ENERGY = 10000

    evolutionduprix = []

    evolutionduprix.append(ENERGY)
    # affichage(evolutionduprix)

    while True:
        transaction, t = marketQueue.receive()
        transaction = transaction.decode()
        type = str(transaction[0])
        transaction = transaction[1:]
        if PRIX < 4:
            PRIX = 11
            print("Inflation des prix à cause d'une catastrophe naturelle !")
        elif PRIX > 18:
            PRIX = 9
            print("Ajustement suite aux Gilets Jaunes !")
        if t == 999: #| type == 992 | type == 999:
            try:
                transaction = int(transaction)
            except:
                transaction = float(transaction)
            if (transaction):
                if type == "a":
                    evolutionduprix.append((ENERGY))
                    # affichage(evolutionduprix)

                    with secondmutex:
                        PRIX = PRIX * (1 - transaction * 0.01)

                elif type == "v":
                    evolutionduprix.append((ENERGY))
                    # affichage(evolutionduprix)

                    with secondmutex:
                        PRIX = PRIX * (1 + transaction * 0.01)

                elif type == "e":
                    with secondmutex:
                        PRIX = PRIX * transaction
                        # affichage(evolutionduprix)


def underprice():
    pass


def upprice(sig, frames):
    marketQueue = sysv_ipc.MessageQueue(100)  # connexion à la messaque Queue du process price

    externalcoefprice = 1.0
    tab = ["major law change", "medium law change", "minor law change", "natural disaster"]
    event = random.choice(tab)
    if event == "minor law change": externalcoefprice = externalcoefprice * random.uniform(1, 1.1)
    if event == "medium law change": externalcoefprice = externalcoefprice * random.uniform(1, 1.2)
    if event == "major law change": externalcoefprice = externalcoefprice * random.uniform(1, 1.3)
    if event == "natural disaster": externalcoefprice = externalcoefprice * random.uniform(1, 1.5)
    externalcoefprice = round(externalcoefprice, 2)
    price = ("e"+str(externalcoefprice)).encode()
    marketQueue.send(price, type=999)


def downprice(sig, frames):
    externalcoefprice = 1.0
    tab = ["major law change", "medium law change", "minor law change", "natural disaster"]
    event = random.choice(tab)
    if event == "minor law change": externalcoefprice = externalcoefprice * random.uniform(1, 0.9)
    if event == "medium law change": externalcoefprice = externalcoefprice * random.uniform(1, 0.8)
    if event == "major law change": externalcoefprice = externalcoefprice * random.uniform(1, 0.7)
    if event == "natural disaster": externalcoefprice = externalcoefprice * random.uniform(1, 0.5)
    externalcoefprice = round(externalcoefprice, 2)
    price = ("e"+str(externalcoefprice)).encode()
    marketQueue.send(price, type=999)

# Partie signal reçu ----------------------------------------------------

# Partie external process ----------------------------------------------------

def external(externalprice, data_ready):
    while True:
        time.sleep(1)
        change = random.uniform(0, 1)
        if change > 0.48:
            os.kill(os.getppid(), signal.SIGUSR1)

        else:
            os.kill(os.getppid(), signal.SIGUSR2)


# Partie Affichage ----------------------------------------------------

def affichage(tableau):
    evolution = ""
    global PRIX

    if len(tableau) > 1:

        if tableau[len(tableau) - 1] > tableau[len(tableau) - 2]:
            evolution = "++"
        elif tableau[len(tableau) - 1] < tableau[len(tableau) - 2]:
            evolution = "--"
        else:
            evolution = ""
        pass

    print("-------------------------------------------------")
    print("Bienvenue sur l'interface d'observation du marché")
    print("                --                |    ")
    print("Cours de l'energie                |   ", evolution, tableau[len(tableau) - 1])
    print("                --                |    ")
    print("Prix                              |          ", round(PRIX, 2))
    print("                --                |    ")
    print("Maisons connectées au marché      |       ", len(connectedHome))
    print("                --                |    ")
    print("--------------------------------------------------")


# Partie Main ----------------------------------------------------

def authentification():
    global connectedHome
    while True:
        connection, type = marketQueue.receive(type=100)
        if type == 100:
            connection.decode()
            connection = str(connection)
            connection = connection.replace('b', '')
            connection = connection.replace('b', '\'')
            print("un nouvel utilisateur s'est connecté, c'est : ", connection)
            connectedHome.append(connection)
        if type == 101:
            connection.decode()
            # connectedHome.remove()

def animate(i):
    pullData = open("new.txt", "r").read()
    dataArray = pullData.split('\n')
    yar = []
    xar = []
    for eachLine in dataArray:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xar.append(int(x))
            yar.append(round(float(y)))
    ax1.clear()
    ax1.plot(xar, yar)
    plt.xlabel('TEMPS')
    plt.ylabel('PRIX')
    plt.title('PRIX DE L\' ÉNERGIE')


def updateValue():
    file = open("new.txt", "w")
    file.write("")
    file.close()

    i = 0
    ind= 0
    while True:
        global PRIX
        if ind > 40:
            file = open("new.txt", "w")
            file.write("")
            file.close()
            ind = 0
        file = open("new.txt", "r")
        debut = file.read()
        file.close()
        # print("1")
        i = i + 1
        time.sleep(1)
        # print("2")
        file = open("new.txt", "w")
        file.write(debut + "\n" + str(i) + "," + str(round(PRIX,2)))
        file.close()
        ind = ind + 1

if __name__ == "__main__":

    global connectedHome
    connectedHome = []

    global PRICE
    PRICE = 10

    signal.signal(signal.SIGUSR1, upprice)
    signal.signal(signal.SIGUSR2, downprice)

    global ENERGY

    externalprice = Queue()
    data_ready = threading.Event()
    # signal.signal(signal.SIGUSR1, handler)

    entities = [
        Thread(target=authentification),
        Thread(target=price, args=(externalprice, data_ready)),
        Thread(target=achat),
        Thread(target=vente),
        Process(target=external, args=(externalprice, data_ready)),
    ]

    t = Thread(target=updateValue)
    t.start()
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ani = animation.FuncAnimation(fig, animate, interval=1000)

    for p in entities:
        p.start()

    plt.show()

    # affichage()

    for p in entities:
        p.join()
