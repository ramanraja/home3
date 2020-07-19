# Hub web server to interact with mobile app
# POST a json payload to http://127.0.0.1:5000/xxx

from flask import Flask, jsonify, abort
from flask import request, make_response
import HubData 

app = Flask("Hub server")

@app.route('/', methods=['GET'])
def index():
    print ('Request: ', request)
    return jsonify({'Welcome to Intof Hub Version' : 1.0})


@app.route('/echo', methods=['GET','POST'])
def echo_input():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'input json is NULL'})
    print (request.json)
    return (request.json)

    

@app.route('/get/time', methods=['GET'])
def time():
    print ('Request: ', request)
    return jsonify({'local time' : db.getTimeStamp ()})
    
    
@app.route('/create/tables', methods=['GET'])
def create_all_tables ():
    print ('Request: ', request)
    try:
        for sql in HubData.CREATE_SQLS:
            db.createTable (sql)
            print ("Table created.")                  
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return jsonify({'error' : str(e)})     
    return jsonify({'result' : 'tables created'})
        
        
@app.route('/delete/tables', methods=['GET'])        
def remove_all_tables():
    print ('Request: ', request)
    try:
        for sql in HubData.DROP_SQLS:
            db.removeTable (sql)
            print ("Table removed.")              
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return jsonify({'error' : str(e)})     
    return jsonify({'result' : 'tables removed'}) 
                
    
@app.route('/list/tables', methods=['GET'])        
def list_tables():
    print ('Request: ', request)
    tables = []
    try:
        rows = db.listTables()
        print (rows)
        print (type(rows))
        for r in rows:
            tables.append (r[0])   # each r is a complete row object containing a single column       
    except Exception as e:
        print ('ERROR: ', str(e)) 
        return jsonify({'error' : str(e)})     
    return jsonify({'tables' : tables}) 
    
        
@app.route('/insert/config', methods=['GET','POST'])
def insconfig():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'config object is NULL'})
    try:
        print (request.json)
        rowid = db.insertConfig ((request.json['config_id'], request.json['config_item']))
        if (rowid < 0):
            return jsonify({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return jsonify({'error' : str(e)})
    return jsonify({'rowid' : rowid})            
    
    
@app.route('/insert/device', methods=['GET','POST'])
def insdevice():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'device object is NULL'})
    try:
        print (request.json)
        rowid = db.insertDevice (request.json)
        if (rowid < 0):
            return jsonify({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return jsonify({'error' : str(e)})
    return jsonify({'rowid' : rowid})      
    
    
@app.route('/insert/device-type', methods=['GET','POST'])
def insdevicetype():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'device type is NULL'})
    try:
        print (request.json)
        rowid = db.insertDeviceType (request.json)
        if (rowid < 0):
            return jsonify({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return jsonify({'error' : str(e)})
    return jsonify({'rowid' : rowid})     
        
    
@app.route('/insert/device-data', methods=['GET','POST'])
def insdevicedata():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'device data is NULL'})
    try:
        print (request.json)
        rowid = db.insertDeviceData (request.json)
        if (rowid < 0):
            return jsonify({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return jsonify({'error' : str(e)})
    return jsonify({'rowid' : rowid})         
    
    
@app.route('/insert/device-event', methods=['GET','POST'])
def insdeviceevent():
    print ('Request: ', request)
    if request.json is None:
        return jsonify({'error' : 'device event is NULL'})
    try:
        print (request.json)
        rowid = db.insertDeviceEvent (request.json)
        if (rowid < 0):
            return jsonify({'error' : 'invalid data'})
    except Exception as e:
        print (str(e))
        return jsonify({'error' : str(e)})
    return jsonify({'rowid' : rowid})    
#-----------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------

db_file_name = r"data\HomeAutomation.db"    #  .\data folder must exist already
db = HubData.HubDB (debug=True)
if not db.connect (db_file_name):
    print ('Invalid database path: {}'.format(db_file_name)) 
    print ('Ensure that the folder exists under the web server home.')
    print ('\n* Cannot start Web Server. *')
else:
    print("local time:")
    print(db.getTimeStamp ())    
    app.run(host="0.0.0.0", debug=True)
    
    
'''-----------------------------------------------------------------
http://127.0.0.1:5000/get/time
http://127.0.0.1:5000/insert/config
http://127.0.0.1:5000/create/tables
http://127.0.0.1:5000/delete/tables
http://127.0.0.1:5000/insert/device
http://127.0.0.1:5000/insert/device-data
http://127.0.0.1:5000/insert/device-type
http://127.0.0.1:5000/insert/device-event
-----------------------------------------------------------------'''    

 