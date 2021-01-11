import random
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

def animate(i):
    pullData = open("sampleText.txt","r").read()
    dataArray = pullData.split('\n')
    yar = []
    yar2 = []
    xar = []
    xar2 = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
            xar2.append(int(x)+1)
            yar2.append(int(y)*-1)
    ax1.clear()
    ax1.plot(xar,yar)
    ax1.plot(xar, yar2)

def updateValue():
    file = open("sampletext.txt", "w")
    debut = file.write("")
    i = 0
    while i < 10:
        file = open("sampletext.txt", "r")
        debut = file.read()
        file.close()
        print("1")
        i = i + 1
        time.sleep(1)
        print("2")
        file = open("sampletext.txt", "w")
        file.write(debut + "\n"+str(i)+","+str(i*i))
        file.close()

t = Thread(target=updateValue)
t.start()
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

