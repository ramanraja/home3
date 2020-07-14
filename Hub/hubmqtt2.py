# MQTT client - Subscriber & Publisher
# Mainly acts as a time server and data logger for the 8266 devices
# test it with IoTRelay*.ino on 8266
# continuously sends messages and also receives
# pip install paho-mqtt

import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import json
import time
import sys

#------------------------------ globals ------------------------------
# server = 'broker.mqtt-dashboard.com'  # http://www.hivemq.com/demos/websocket-client/
server = 'test.mosquitto.org'      
port = 1883
client = None
sub_topic = "abc/def/status/Grp0/+"
ORG_NAME = 'abc'    # any topic must start with this string

#------------------------------ callbacks ---------------------------- 
topic = "sender"
time_flag = False
log_file = None

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT server.')
    client.subscribe (sub_topic, qos=0)  # on reconnection, automatically renew
 
def on_publish(client, userdata, mid):
    print("Published msg id: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed; mid="+str(mid)+", granted QOS="+str(granted_qos))
    
def on_message(client, userdata, msg):
    global topic, time_flag, log_file
    message = msg.payload.decode('utf-8')
    print(msg.topic + " -> " + message) 
    #print (type(message))
    jmessage = json.loads(message)
    #print (type(jmessage))
    #print (jmessage)
    if  ('REQ' in jmessage and jmessage['REQ'] == "TIME"):
        topic = msg.topic
        time_flag = True
        return
    if ('DAT' in jmessage):
        light = jmessage['DAT']['LIGHT']
        now = datetime.now()
        clock_time = now.strftime("%H:%M")   
        device = msg.topic.split('/')[-1]     
        log_entry = "{},{},{}\n".format (clock_time,device,light)
        print(log_entry)
        log_file.write (log_entry)
        log_file.flush()
        
    
#---------------------------- main -----------------------------------
terminate = False

today = datetime.now().strftime("Log_%d-%m-%y.csv")
print ("log file:", today)
log_file = open(today, "a+")
     
# note: if client ID is constant, earlier subscriptions will still linger *     
client = mqtt.Client("raman_rajas_client_1963", clean_session=False)  # True
# client.username_pw_set("User", "password")     

client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

print('Connecting to MQTT server: ' +server)
client.connect(server, port, keepalive=60)    # blocking call
#client.connect_async(server, port, keepalive=60)  # non blocking
#######client.subscribe (topic2, qos=0)  # do that in on_connect() !

# blocking call - reconnects automatically (useful esp. for mqtt listeners)
#client.loop_forever()    # blocking call

client.loop_start()       # start a background thread (useful if you are also an mqtt sender)
time.sleep(2)
print ('Press ^C to quit...')
  
try:
    while not terminate:
        if (not time_flag):  # this is the mutex
            continue
        time_flag = False;
        if  not topic.startswith (ORG_NAME):
            print ('--- Invalid topic ---')
            continue
        pub_topic = topic.replace("status", "cmd")
        print (pub_topic)
        now = datetime.now()
        clock_time = now.strftime("#%H:%M")
        print (clock_time)
        (rc, mid) = client.publish (pub_topic, payload=clock_time, qos=0, retain=False)
 
except KeyboardInterrupt:
    print ('<break>')
    terminate = True
      
print ('Stopping client loop..')      
client.loop_stop()   # kill the background thread   
client.disconnect()
log_file.close()
time.sleep(1)   
print ('Main thread quits.')   
