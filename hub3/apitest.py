import json
import random
import requests
from time import sleep
'''
http://127.0.0.1:5000/
http://127.0.0.1:5000/get/time
http://127.0.0.1:5000/echo

http://127.0.0.1:5000/delete/tables
http://127.0.0.1:5000/create/tables
http://127.0.0.1:5000/list/tables

http://127.0.0.1:5000/register/mobile
http://127.0.0.1:5000/insert/app/config
http://127.0.0.1:5000/get/app/config

http://127.0.0.1:5000/update/device/types
http://127.0.0.1:5000/update/room/types

http://127.0.0.1:5000/list/hardware/types
http://127.0.0.1:5000/list/device/types
http://127.0.0.1:5000/list/room/types

http://127.0.0.1:5000/self/register/device
http://127.0.0.1:5000/insert/device

http://127.0.0.1:5000/discover/devices
http://127.0.0.1:5000/list/active/devices
http://127.0.0.1:5000/list/inactive/devices    

http://127.0.0.1:5000/provision/device
http://127.0.0.1:5000/get/device/config
http://127.0.0.1:5000/update/device/config
http://127.0.0.1:5000/device/exists
http://127.0.0.1:5000/delete/device

http://127.0.0.1:5000/insert/device/data
http://127.0.0.1:5000/get/device/data
http://127.0.0.1:5000/insert/device/status
http://127.0.0.1:5000/get/device/status
http://127.0.0.1:5000/insert/device/event
http://127.0.0.1:5000/get/device/event 
'''


HTTP_OK = requests.codes.ok
RAND_MAC = None
TEST_MAC1 = 'AA1090C0810E'
TEST_MAC2 = 'BB2089F4021C'
NON_EXIST_MAC = "FFFFF0EEEE"

def get_it (url, payload=None):
    try:
        print ('GET ', url)
        res = requests.get(url, params=payload)  #,headers=headers
        print (res.status_code)
        if (res.status_code != HTTP_OK):
            print ("HTTP error: {}".format (res.status_code)) 
            res.raise_for_status() 
        else:
            print (res.json())
    except Exception as e:
        print(e)
        print()
        
def get_it_cookie (url, payload=None, cookie=None):
    coo = {'my_cookie_name' : 'this is my cookie'}
    res = requests.get(url, params=payload, cookies=coo)  #,headers=headers
    if (res.status_code != HTTP_OK):
        print ("HTTP error: {}".format (res.status_code)) 
        res.raise_for_status() 
    else:
        print (res.json())
        if res.cookies.get ('my_cookie_name'):
            print ('got a cookie: ', res.cookies['my_cookie_name'])
    print()
    
def post_it (url, payload):
    jheader = {"content-type" : "application/json"}
    res = requests.post(url, json=payload, headers=jheader)
    if (res.status_code != HTTP_OK):
        print ("HTTP error: {}".format (res.status_code))  
    else:
        print (res.json())
    print()
#---------------------------------------------------------------------------------

def get_root():
    print('root..')
    url = 'http://127.0.0.1:5000/'
    payload = None
    get_it (url, payload)  
    
def get_time():
    print('time..')
    url = 'http://127.0.0.1:5000/get/time'
    payload = None
    get_it_cookie (url, payload)    
        
def echo_test():
    print('echo_test..')
    url = 'http://127.0.0.1:5000/echo'  
    payload = {'Testing':'echo', 'Name':'Raja', 'Age':45, 'Nums':[20,10,70]}
    post_it (url, payload)  
            
def delete_create_list_tables():
    print('del_cre_lis_tables..')
    url = 'http://127.0.0.1:5000/delete/tables' 
    payload = None
    get_it (url, payload)          
    url = 'http://127.0.0.1:5000/create/tables' 
    payload = None
    get_it (url, payload)   
    url = 'http://127.0.0.1:5000/list/tables' 
    payload = None
    get_it (url, payload)       
#------------------------------------------------------------------------------------

def register_mobile():
    print('register_mobile..')
    url = 'http://127.0.0.1:5000/register/mobile'
    payload = {
        'user_id' : 'ajax@coriolis.com',
        'app_id' : 'intof_home_app',
        'version' : '1.0'
    }
    post_it (url, payload)  

def insert_app_config ():
    global APP_CONFIG_ID
    print ('insert_app_config..')
    url = 'http://127.0.0.1:5000/insert/app/config'
    APP_CONFIG_ID = 'confid_{}'.format (random.randint(0,1000))
    payload = { 
                  "config_id" : APP_CONFIG_ID, 
                  "config_item" : {
                        "org_id" : "myorg",
                        "hub_name"  : "HUB1",
                        "hub_ap"    : "HUB1_AP",
                        "hub_ap_passwd" : "hubpassword",
                        "wifi_ap" : "wifiap",
                        "wifi_ap_passwd" : "wifipasswd",
                        "user_name" : "abc@gmail.com",
                        "user_pwd"  : "userpasswd",
                        "email"     : "def@gmail.com",
                        "mobile"    : "9898989898",
                        "location"  : "myhome",
                        "ota_server" : "http://192.168.4.100:8000/ota",
                        "web_server" : "http://192.168.4.100:7000/"
                   }
               }
    post_it (url, payload)  
    
def get_app_config_GET():  
    print ('get_app_config [GET]..')
    url = 'http://127.0.0.1:5000/get/app/config' 
    payload = {'config_id' :  APP_CONFIG_ID}  # NOTE: this can be sent as a URL parameter
    get_it (url, payload)
    
def get_app_config_POST():
    print ('get_app_config [POST]..')
    url = 'http://127.0.0.1:5000/get/app/config'
    payload = {'config_id' :  APP_CONFIG_ID}
    post_it (url, payload)

#--------------------------------------------------------------

def insert_device_types():
    update_device_types()
    
def update_device_types():
    print('Updating device types..')
    dt = {  'device_types': 
        ['Smoke detector',  'Pump', 'Bulb', 'CO2 alarm', 'Others']
    }
    http://127.0.0.1:5000/update/device/types
    print (retval)
    print()
            
def list_device_types():
    print('Device types:')
http://127.0.0.1:5000/list/device/types
print(retval)
    print ()
    
    
def insert_room_types():
    update_room_types()

def update_room_types():
    print('Updating room types..')
    rt = {  'room_types': 
         ['Drawing room',  'Mini Hall', 'Kitchen', 'Pooja room', 'Others']    }
http://127.0.0.1:5000/update/room/types
    print (retval)
    print()
        
def list_room_types():
    print('Room types:')
     http://127.0.0.1:5000/list/room/types
    print (retval)
    print ()
    
# this is collected only from the devices table, so no insert/update    
def list_hardware_types():    
    print ('Hardware types:')
    http://127.0.0.1:5000/list/hardware/types
    print(retval)
    print()     
#--------------------------------------------------------------
    
def self_register_device(): # only from device
    print ('Device: self-registering ...')
    url =    'http://127.0.0.1:5000/self/register/device'    
    new_min_dev1 = {'device_id':TEST_MAC1, 'hardware_type':'REL4.1-PIR-RAD', 'num_relays':4}
    new_min_dev2 = {'device_id':TEST_MAC2, 'hardware_type':'REL2.0', 'num_relays':2}
    retval = post_it (url, new_min_dev1)
    print (retval)
    retval = post_it (url, new_min_dev2)
    print (retval)    
    print()
        
def direct_insert_device(): # only from back end
    global RAND_MAC
    print ('Directly provisioning new device...')
    RAND_MAC = ''.join(random.choice('0123456789ABCDEF') for n in range(10))
    jhardware_conf = {'group_id':'G0', 'primary_relay':1, 'active_low':0, 
        'auto_off_min':2.5, 'status_freq':5}
    payload = {'device_id':RAND_MAC, 'hardware_type':'REL4.3-TEM', 'num_relays':4,
        'room_name':'Grandma\'s room', 'room_type' : 'Bed Room',
        'enabled':1, 'hardware_config': json.dumps (jhardware_conf)}    
    print (payload)
    url = 'http://127.0.0.1:5000/insert/device'
    retval = post_it (url, payload)
    print (retval)
    print()    
    
def discover_devices():
    print ('discovering new_devices..')
    url = 'http://127.0.0.1:5000/discover/devices'
    get_it (url)
    print (retval)
    print()    
    
def  list_active_devices(): 
http://127.0.0.1:5000/list/active/devices    
    get_it (url)
    print (retval)
    print() 
    
def  list_inactive_devices(): 
http://127.0.0.1:5000/list/inactive/devices    
    get_it (url)
    print (retval)
    print()     
#------------------------------------------------------------


def provision_device():  # this is actually onboarding the device
    print ('Provisioning non existent device..')
    http://127.0.0.1:5000/provision/device
    provision_params1 = {
        'device_id' : 'ABCDEFG0000',
        'room_name' : 'Bust room',
        'room_type' : 'Unknown room type'
    }
    retval = post_it (url, payload)
    print (retval)
    print() 
    print ('Provisioning real device..')
    provision_params2 = {
        'device_id' : TEST_MAC1,
        'room_name' : 'Kutty\'s bed room',
        'room_type' : 'Bed room'
    }
    retval = post_it (url, payload)
    print (retval)
    print()   
 
    
def get_device_config():
    print ('Device config:')
    http://127.0.0.1:5000/get/device/config
    dc = maria.getDeviceConfig ({'device_id':'non-existant'})
    retval = get_it (url, payload)
    print (retval)
    print() 
    dc = maria.getDeviceConfig ({'device_id':TEST_MAC3})
    retval = get_it (url, payload)
    print (retval)
    print() 
    
    
def set_device_config():
    print ('Inserting device config..')
    http://127.0.0.1:5000/update/device/config
    dc1 = {'name':'Hall light',     'type' : 'Light', 'schedule':[18,30,6,0]}
    dc2 = {'name':'Bed room A/C',   'type' : 'A/C',   'schedule':[20,0,5,40]}
    dc3 = {'name':'Hall fan',       'type' : 'Fan',   'schedule':[]}
    dc4 = {'name':'Portico light',  'type' : 'Light', 'schedule':[14,30,7,10]}
    dev_con = {
        'device_id':TEST_MAC1,   # TEST_MAC2 here should raise an exception
        'room_name' : 'Basement',
        'room_type' : 'Garage',
        'device_config' : [dc1, dc2, dc3, dc4]
    }
    retval = post_it (url, payload)
    print (retval)
    print()         
    
def device_exits(): 
    print ('Device existence:')
    http://127.0.0.1:5000/device/exists
    retval = get_it (url, TEST_MAC1)
    print (retval)
    print()       
    retval = get_it (url, TEST_MAC2)
    print (retval)
    print()      
    retval = get_it (url, 'no-such-dev')
    print (retval)
    print()  
        
def delete_device():
    print('Deleting device..')
    http://127.0.0.1:5000/delete/device
    retval = get_it (url, 'no-such-dev')
    print (retval)
    print()  
        
     
#------------------------------------------------------

def set_device_data():
    print ('Setting device data..')
    http://127.0.0.1:5000/insert/device/data
    simul_data = {"LIGHT":456, "TEMP":23, "HUMI":76}
    dev_data = {'device_id':TEST_MAC2, 'relay_status':'0101', 'data':simul_data} 
    maria.insertDeviceData (dev_data)   
    print ()
    
def get_device_data():
    print ('getting device data:')
    http://127.0.0.1:5000/get/device/data
    retval = get_it (url, 'TEST_MAC1')
    print (retval)
    print() 
    retval = get_it (url, 'no-such-dev')
    print (retval)
    print() 
        
def set_device_status():        
http://127.0.0.1:5000/insert/device/status
payload ={'device_id':TEST_MAC2, 'relay_status':'0101'}
    retval = post_it (url, payload)
    print (retval)
    print() 


def get_device_status():
http://127.0.0.1:5000/get/device/status
    retval = get_it (url, 'TEST_MAC1')
    print (retval)
    print() 
             
def set_device_event():
    print ('inserting event..')
    http://127.0.0.1:5000/insert/device/event
    eve_body = {'update':'failed', 'reason':'HTTP', 'code':400}
    dev_event = {'device_id':TEST_MAC1, 'event_type':'FW_UPDATE', 'event_body':eve_body}
    retval = post_it (url, payload)
    print (retval)
    print() 
    
def get_device_event():
    print ('Device event:')
    http://127.0.0.1:5000/get/device/event 
    event = maria.getDeviceEvent({'device_id':TEST_MAC1})
    retval = get_it (url, payload)
    print (retval)
    print()    
#-----------------------------------------------
# MAIN
#------------------------------------------------
APP_CONFIG_ID = None

print('\nAPI tester starting..')
get_root()
get_time()

echo_test()
delete_create_list_tables()

register_mobile()

insert_app_config()
get_app_config_GET()
get_app_config_POST()

insert_device_types()
insert_room_types()

list_hardware_types
list_device_types()
list_room_types
 
register_new_device() 
direct_insert_device() 
discover_new_devices()

provision_device()
set_device_config()
get_device_config()

get_device_data()
set_device_data()
get_device_data()

get_device_status()
set_device_status()
get_device_status()

set_device_event()
get_device_event()   

list_active_devices() 
delete_device()
list_active_devices()  


print('\nBye!')



