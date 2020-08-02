# THIS IS WORK IN PROGRESS; NEEDS LOT OF CHANGES

# Flask web server running on the hub to interact with mobile app
# POST a json payload to http://127.0.0.1:5000/xxx
# TODO:
#  Integrate Flask-MQTT 
#  Decorator @require_login and @require_admin for the admin functions like create_tables()
#  button press to trigger register_device mode for 60 seconds
#  Add @require_login to check validity of token
#  get_device_schedule(mac_id),  set_device_schedule(), get_all_schedules()
#  Maintain a schedule for every relay. There will be a flag 'daily'=yes (or no for one time event)
#  MQTT client calls get_schedules() at every hour and fires on/off events  accordingly
#  Maintain a list of devices that are online (use python 'Set' data type) ; this is culled from the
#     events and data packets; some of them may be new devices waiting to be configured
#  Add a /list/devices/debug method. This will return additional information like
#     hardware and firmware version for the devices

# pip uninstall jwt   # this is the wrong package ! UNINSTALL it, if present
# pip install pyjwt   # install this package

import jwt
from flask import Flask,abort
from flask import request, make_response
from datetime import datetime, timedelta
import PasswordStore
import MariaWrapper  

app = Flask("Intof Hub")
# TODO: add if(debug): every where

@app.route('/', methods=['GET'])
def index():
    if debug: print ('Request: ', request)
    return ({'message' : 'Welcome to Intof Hub', 'version' : '1.0'})


@app.route('/echo', methods=['GET','POST'])
def echo_input():
    if debug: print ('Request: ', request)
    if request.json is None:
        return ({'error' : 'input json is NULL'})
    print (request.json)
    return (request.json)

    
@app.route('/get/time', methods=['GET'])
def time():
    if debug: print ('Request: ', request)
    return ({'local_time' : db.getTimeStamp ()})
    
    
# TODO: the following calls need admin access decorator    
@app.route('/create/tables', methods=['GET'])
def create_all_tables ():
    if debug: print ('Request: ', request)
    try:
        for sql in HubData.CREATE_SQLS:
            db.createTable (sql)
            print ("Table created.")                  
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return ({'error' : str(e)})     
    return ({'result' : 'tables created'})
        
        
@app.route('/delete/tables', methods=['GET'])        
def drop_all_tables():
    if debug: print ('Request: ', request)
    try:
        db.dropTables()
        if debug: print ("all tables removed.")              
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return ({'error' : str(e)})     
    return ({'result' : 'tables removed'}) 
                
    
@app.route('/list/tables', methods=['GET'])        
def list_tables():
    if debug: print ('Request: ', request)
    tables = []
    try:
        rows = db.listTables()
        print (rows)
        print (type(rows))
        for r in rows:
            tables.append (r[0])   # each r is a complete row object containing a single column       
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return ({'error' : str(e)})     
    return ({'tables' : tables})     
#-------------------------------------------------------------------------------------------------------    
    
@app.route('/register/mobile', methods=['GET','POST'])
def register_mobile(): 
    if debug: print ('Request: ', request)
    if request.json is None:
        return ({'error' : 'input json is NULL'})
    jtoken = {}
    jtoken['code'] = 200    
    payload = {}
    if 'user_id' in request.json:
        payload['user_id'] = request.json['user_id']
    else:
        jtoken ['registration'] = 'failure'
        jtoken ['error'] = 'user id is required'
        return  (jtoken)    
    if 'app_id' in request.json:
        payload['app_id'] = request.json['app_id']
    else:
        jtoken ['registration'] = 'failure'
        jtoken ['error'] = 'app id is required'
        return  (jtoken)     
    if 'version' in request.json:
        payload['version'] = request.json['version']
    else:
        payload['version'] = '1.0'
    try :
        payload['hub_id'] = PasswordStore.hub_id
        expiry_date = datetime.now() + timedelta(days=PasswordStore.jwt_life_time)
        payload ['exp'] = expiry_date
        token = jwt.encode (payload, PasswordStore.jwt_secret, PasswordStore.jwt_algorithm)
        token = token.decode('utf-8')
        print (token)
        jtoken ['registration'] = "success"
        jtoken ['token'] = token
        jtoken['expiry'] = expiry_date
        return  (jtoken)
    except Exception as e:
        jtoken ['registration'] = 'failure'
        jtoken ['error'] = str(e)
        return  (jtoken)
    
#-------------------------------------------------------------------------------------------------------    
        
@app.route('/insert/config', methods=['GET','POST'])
def insconfig():
    if debug: print ('Request: ', request)
    if request.json is None:
        return ({'error' : 'config object is NULL'})
    try:
        print (request.json)
        rowid = db.insertConfig ((request.json['config_id'], request.json['config_item']))
        if (rowid < 0):
            return ({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return ({'rowid' : rowid})            
    
    
# This is for admin use; to add a fully provisioned device through a back end job 
@app.route('/insert/device', methods=['POST'])
def insert_device():
    try:
        print (request.json)
        rowid = db.insertDevice (request.json)
        if (rowid < 0):
            return ({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return ({'rowid' : rowid})      
  
  
# this is called by the mobile, after the *hub* has discovered a set of new devices
@app.route('/discover/devices', methods=['GET'])        
def list_new_devices ():
    try:
        print (request.json)
        rows = db.discoverNewDevices (limit=20)
        if rows is None:
            return ({'status' : 'No new devices'})
        devices = []
        for row in rows:
            device = {}
            device ['device_id'] = row[0]
            device ['type'] = row[1]
            devices.append (device)
        discovered = {'devices' : devices}
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return  (discovered) 
    
  
@app.route('/list/devices', methods=['GET'])        
def list_active_devices ():
    try:
        print (request.json)
        rows = db.getActiveDevices (limit=50)
        if rows is None:
            return ({'status' : 'No active devices'})
        devices = []
        for row in rows:
            device = {}
            device ['device_id'] = row[0]
            device ['type'] = row[1]
            devices.append (device)
        active_devices = {'devices' : devices}
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return  (active_devices)   
    
    
@app.route('/insert/device-type', methods=['POST'])
def insdevicetype():
    try:
        print (request.json)
        rowid = db.insertDeviceType (request.json)
        if (rowid < 0):
            return ({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return ({'rowid' : rowid})     
        
    
@app.route('/insert/device-data', methods=['GET','POST'])
def insdevicedata():
    if debug: print ('Request: ', request)
    if request.json is None:
        return ({'error' : 'device data is NULL'})
    try:
        print (request.json)
        rowid = db.insertDeviceData (request.json)
        if (rowid < 0):
            return ({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return ({'rowid' : rowid})         
    
    
@app.route('/insert/device-event', methods=['GET','POST'])
def insdeviceevent():
    if debug: print ('Request: ', request)
    if request.json is None:
        return ({'error' : 'device event is NULL'})
    try:
        print (request.json)
        rowid = db.insertDeviceEvent (request.json)
        if (rowid < 0):
            return ({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return ({'error' : str(e)})
    return ({'rowid' : rowid})    
#-----------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------

debug = True
db = MariaWrapper.MariaWrapper (debug=True)
if not db.connect ():
    print ('\n** Failed to connect to MariaDB database **') 
    print ('\n* Cannot start Web Server. *')
else:
    print("local time:")
    print(db.getTimeStamp ())    
    app.run(host="0.0.0.0", debug=True)
    
    
'''-----------------------------------------------------------------
http://127.0.0.1:5000/
http://127.0.0.1:5000/get/time
http://127.0.0.1:5000/echo
http://127.0.0.1:5000/insert/config
http://127.0.0.1:5000/create/tables
http://127.0.0.1:5000/delete/tables
http://127.0.0.1:5000/insert/device
http://127.0.0.1:5000/insert/device-data
http://127.0.0.1:5000/insert/device-type
http://127.0.0.1:5000/insert/device-event
-----------------------------------------------------------------'''    

 