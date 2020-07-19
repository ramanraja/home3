# MQTT client - Subscriber & Publisher
# Acts as a time server and data logger for the 8266 devices
# receives data from devices and sends it to Intof web service for storage
# test it with IoTRelay*.ino on 8266

# pip install paho-mqtt

import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import requests
import json
import time
import sys

#------------------------------ globals ------------------------------
# server = 'broker.mqtt-dashboard.com'  # http://www.hivemq.com/demos/websocket-client/
# server = 'm2m.eclipse.org'
# server = 'test.mosquitto.org'
# server = 'localhost'                  # mosquitto -v
# port = 8000

server = 'broker.mqttdashboard.com'     # http://www.hivemq.com/demos/websocket-client/
port = 1883
client = None
sub_topic = "intof/home/status/G0/+"
ORG_NAME = 'intof'  # any topic must start with this string
#hub_url = 'http://192.168.0.101:5000/echo'  
hub_url = 'http://192.168.0.101:5000/insert/device-data'  
jheader = {"content-type":"application/json"}

#------------------------------ post to hub ---------------------------- 

def post_it (jpayload) :
    try:
        print ("sending: {}".format(jpayload))
        response = requests.post (hub_url, json=jpayload, headers=jheader)
        print ('Response code: ', response.status_code)
        print (response.text)
        if (response.status_code != 200):
            print ("--- HTTP error code {} ---".format (response.status_code))          
    except Exception as e:
        print (e)

#------------------------------ callbacks ------------------------------

topic = "sender"
time_flag = False
jpayload = {}

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT server.')
    client.subscribe (sub_topic, qos=0)  # on reconnection, automatically renew
 
def on_publish(client, userdata, mid):
    print("Published msg id: "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed; mid="+str(mid)+", granted QOS="+str(granted_qos))
    
def on_message(client, userdata, msg):
    global topic, time_flag, jpayload
    message = msg.payload.decode('utf-8')
    print(msg.topic + " -> ", message) 
    #print (type(message))
    jmessage = json.loads(message)
    #print (type(jmessage))
    #print (jmessage)
    if  ('REQ' in jmessage and jmessage['REQ'] == "TIME"):
        topic = msg.topic
        time_flag = True  # the main thread will now send the time to device
        return
    if ('DAT' in jmessage):  # names of the following variables must be in sync with hubServer.py
        jpayload['relay_status'] = jmessage['STA']  
        jpayload['data'] = jmessage['DAT'] # this is an inner json
        jpayload['time_stamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")   
        jpayload['MAC'] = msg.topic.split('/')[-1]     
        post_it (jpayload)
    
#---------------------------- main -----------------------------------

terminate = False
     
# note: if client ID is constant, earlier subscriptions may still linger *     
client = mqtt.Client("raman_rajas_client_1963", clean_session=True) # False
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
time.sleep(1)   
print ('Main thread quits.')   
