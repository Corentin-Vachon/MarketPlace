from multiprocessing import Process, Manager
import time
import random
import threading

wheatherTab = {
    'rain': 50.0,
    'sun': 50.0,
    'vynd': 50.0,
    'heat': 50.0,
}
coeffweather = 1

def f():
    global coeffweather
    global wheatherTab
    i = 0
    while True:
        time.sleep(1)
        if i > 10:
            i = 0
            wheatherTab = {
                'rain': 50.0,
                'sun': 50.0,
                'vynd': 50.0,
                'heat': 50.0,
            }
        wheatherTab['rain'] = round(wheatherTab['rain'] * random.uniform(0.95, 1.05),3)
        wheatherTab['sun'] = round(wheatherTab['sun'] * random.uniform(0.95,1.05),3)
        wheatherTab['vynd'] = round(wheatherTab['vynd'] * random.uniform(0.95, 1.05),3)
        wheatherTab['heat'] = round(wheatherTab['heat'] * random.uniform(0.95, 1.05),3)
        #print(wheatherTab)
        coeffweather = ( wheatherTab['rain'] + wheatherTab['sun'] + wheatherTab['vynd'] + wheatherTab['heat'])
        print("MÉTÉO ")
        print('-----------------------------------------------------------------------------------------------')
        print("Coefficient :           :  ",coeffweather/200)
        print('-----------------------------------------------------------------------------------------------')
        print('Météo actuel              :',wheatherTab)
        print('-----------------------------------------------------------------------------------------------')

        i = i + 1

def show():
    return wheatherTab.values()

p = threading.Thread(target=f)
p.start()

from multiprocessing.managers import BaseManager

queue = show()

class QueueManager(BaseManager): pass

QueueManager.register('get_queue', callable=lambda: queue)

m = QueueManager(address=('', 50000), authkey=b'cupteam')
s = m.get_server()
s.serve_forever()


p.join()
