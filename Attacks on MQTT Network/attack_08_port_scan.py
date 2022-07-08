#port scan attack

# import sys
# import os

# os.system('clear')

# ip = "34.125.53.182"
# #Does an Initial NMAP Scan of TCP ports and writes the result to TCPSCAN.xml file
# print("")
# print("++++++++++Starting TCP Protocol Scan +++++++++++++")
# tcpScan = os.system("/usr/bin/nmap -sT -vvv -p- -Pn --webxml -oA TCPSCAN %s" %ip)
# print("++++++++++ END OF TCP Protocol Scan ++++++++++++++")
# pwd = str(os. getcwd())

# #Read the open port list from the TCPSCAN.xml file and store in a variable
# openPorts = os.popen("/bin/cat  $PWD/TCPSCAN.xml | grep 'portid' |cut -d '=' -f 3 | cut -d '>' -f 1 | cut -d '\"' -f 2 ").read()
# print("The list of open ports are: "),
# print(openPorts.split())

#this attack can be further improved, add os scan, protocol wose scanning 

import nmap
import threading

port_min = 1800
port_max = 2000

ip_add = "34.125.53.182"

open_ports = []

def makeScan():
    nm = nmap.PortScanner()
    # Looping over all of the ports in the specified range.
    for port in range(port_min, port_max + 1):
        try:
            result = nm.scan(ip_add, str(port))
            # Uncomment following line and look at dictionary
            # print(result)
            port_status = (result['scan'][ip_add]['tcp'][port]['state'])
            print(f"Port {port} is {port_status}")
        except:
            # Ensures the program doesn't crash when we try to scan some ports that we can't scan.
            print(f"Cannot scan port {port}.")
        
        
        
thread1 = threading.Thread(target=makeScan)
thread2 = threading.Thread(target=makeScan)
thread3 = threading.Thread(target=makeScan)
thread4 = threading.Thread(target=makeScan)


thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()