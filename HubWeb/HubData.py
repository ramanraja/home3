# SQLite wrapper class; mainly to insert data into various IoT tables for the Hub
# It can also create the tables if called.
# Cloned from SQLite4.py and SQLite8.py
# SQLite Same Thread problem: see the discussion at
# https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
# self.connection = sqlite3.connect (db_file_name, check_same_thread=False)

import sys
import json
import sqlite3
import random
from sqlite3 import Error


CREATE_SQL1 = '''CREATE TABLE IF NOT EXISTS config
       (config_id TEXT NOT NULL PRIMARY KEY, config_item TEXT);'''
    
CREATE_SQL2 = '''CREATE TABLE IF NOT EXISTS device
       (MAC TEXT NOT NULL PRIMARY KEY, device_name TEXT, location TEXT, device_type TEXT,
       group_id TEXT, primary_relay INTEGER, active_low INTEGER, status_freq_mins INTEGER,
       auto_off_mins REAL, night_hours TEXT, light_thresholds TEXT, enabled INTEGER, online INTEGER);'''
         
CREATE_SQL3 = '''CREATE TABLE IF NOT EXISTS deviceType 
         (device_type TEXT, version TEXT);'''
    
CREATE_SQL4 = '''CREATE TABLE IF NOT EXISTS deviceData
         (MAC TEXT NOT NULL, time_stamp TEXT, relay_status TEXT, data TEXT, 
         FOREIGN KEY (MAC) REFERENCES device(MAC));'''
    
CREATE_SQL5 = '''CREATE TABLE IF NOT EXISTS deviceEvent
         (MAC TEXT NOT NULL, time_stamp TEXT, event_type TEXT, event_body TEXT, 
         FOREIGN KEY (MAC) REFERENCES device(MAC));'''
   
CREATE_SQLS = [CREATE_SQL1, CREATE_SQL2, CREATE_SQL3, CREATE_SQL4, CREATE_SQL5]

TABLE_NAMES = ['config', 'device', 'deviceType', 'deviceData', 'deviceEvent']

DROP_SQL1 = 'DROP TABLE  config;'
DROP_SQL2 = 'DROP TABLE  device;'
DROP_SQL3 = 'DROP TABLE  deviceType ;'
DROP_SQL4 = 'DROP TABLE  deviceData;'
DROP_SQL5 = 'DROP TABLE  deviceEvent;'
DROP_SQLS = [DROP_SQL1, DROP_SQL2, DROP_SQL3, DROP_SQL4, DROP_SQL5]

LIST_TABLES_SQL = 'SELECT NAME FROM SQLITE_MASTER WHERE TYPE="table"';
 
config_param_list = ['config_id', 'config_item']
 
SQL_INS_CONFIG = '''INSERT INTO  config 
          (config_id, config_item)
          VALUES (?,?);'''
SQL_INS_CONFIG_LEN = 2
SQL_GET_CONFIG = 'SELECT * FROM config  limit ?;'
SQL_GET_CONFIG_ITEM = 'select * from config where config_id=?'
SQL_NUM_ROWS_CONFIG = 'select count (*) from config;'

device_param_list = [    # Do NOT change this order!
    'MAC', 'device_name',  'location', 'device_type',
    'group_id',   'primary_relay',  'active_low',
    'status_freq_mins',  'auto_off_mins', 'enabled', 'online'
]  # there are two more; they are array types
  
# Do NOT change the order of the following parameters!    
SQL_INS_DEVICE = '''INSERT INTO  device 
          (MAC, device_name, location, device_type,
          group_id, primary_relay, active_low, status_freq_mins,
          auto_off_mins, enabled, online, night_hours, 
          light_thresholds)
          VALUES (?,?,?,?  ,?,?,?,?,  ?,?,?,?,  ?);'''
SQL_INS_DEVICE_LEN = 13

SQL_GET_DEVICE = 'select * from device where MAC=?;'

SQL_NUM_ROWS_DEVICE = 'select count (*) from device;'
         
SQL_DELETE_DEVICE = 'DELETE FROM device WHERE MAC=?';
         
device_type_param_list = ['device_type', 'version']
    
SQL_INS_DEVICE_TYPE = '''INSERT INTO deviceType 
          (device_type, version) 
          VALUES (?,?);'''
SQL_INS_DEVICE_TYPE_LEN = 2

device_data_param_list = ['MAC', 'time_stamp', 'relay_status']   # NOTE: there is one more json param, named
                                                                 # 'data' which should be stringified before inserting
              
SQL_INS_DEVICE_DATA = '''INSERT INTO  deviceData
          (MAC, time_stamp, relay_status, data)   
          VALUES (?,?,?,?);''' 
SQL_INS_DEVICE_DATA_LEN = 4 
    
device_event_param_list = ['MAC', 'time_stamp', 'event_type', 'event_body']
    
SQL_INS_DEVICE_EVENT = '''INSERT INTO  deviceEvent
          (MAC, time_stamp, event_type, event_body)
          VALUES (?,?,?,?);''' 
SQL_INS_DEVICE_EVENT_LEN = 4

SQL_GET_TIMESTAMP = 'SELECT datetime("now", "localtime");'
    
#-------------------------------------------------------------------------------

class HubDB():
    debug = False
    connection = None
    cursor = None

    #  if file name is ":memory:" it is created in RAM    
    def __init__(self, debug=False):   
        self.debug = debug
                
                
    def connect (self, db_file_name=":memory:"):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connection = sqlite3.connect (db_file_name, check_same_thread=False)
            self.cursor = self.connection.cursor()
            if (self.debug):
                print ('Connected to DB {}'.format (db_file_name))
            return True
        except Error as e:
            print('Failed to connect to DB: {}'.format(str(e)))
            self.connection = None
            return False


    def close (self):
        if self.cursor:
            self.cursor.close()    
        if self.connection:
            self.connection.close()
        if (self.debug):
            print ('Connection closed.')            
                    
                    
    def getTimeStamp (self):
        self.cursor.execute (SQL_GET_TIMESTAMP);
        ts = self.cursor.fetchone()[0]
        if (self.debug):
            print (ts)    
        return (ts)
#------------------------  

    def createTable (self, creator_sql):
        self.cursor.execute (creator_sql);
            
            
    def removeTableByName (self, table_name):
        if self.debug:
            print ('dropping table: {}'.format(table_name))
        self.cursor.execute ('DROP TABLE "{}";'.format(table_name));    
         
         
    def removeTable (self, remover_sql):
        self.cursor.execute (remover_sql);
            
            
    def listTables (self):
        self.cursor.execute (LIST_TABLES_SQL)
        rows = self.cursor.fetchall()
        return rows;        
#------------------------  


    def insertConfig (self, jconfig):
        if (len(jconfig) != SQL_INS_CONFIG_LEN): 
            print ('insertConfig: invalid data')
            return -1            
        self.cursor.execute (SQL_INS_CONFIG, self.jsonToConfig(jconfig))   
        self.connection.commit()
        return self.cursor.lastrowid
        
        
    def getConfig (self, num_rows=1):
        self.cursor.execute (SQL_GET_CONFIG, (num_rows,)); # NOTE: (num_rows,) has a tuple syntax
        rows = self.cursor.fetchall()
        return rows;
        

    def getConfigItem (self, item_id):
        #print ('fetching: {}'.format(item_id))
        self.cursor.execute (SQL_GET_CONFIG_ITEM, (item_id,)); # OBSERVE: the comma and parenthesis in (item_id,) 
        row = self.cursor.fetchone()
        return row;
        
        
    def getConfigRowCount (self):
        self.cursor.execute (SQL_NUM_ROWS_CONFIG); 
        rows = self.cursor.fetchone()
        return rows[0];        
        
        
    def jsonToConfig (self, jconfig):
        lis = []
        for param in config_param_list:        
            if param in jconfig:
                lis.append (jconfig[param])    
        tup = tuple (lis)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup          
#------------------------            
            
    def insertDevice (self, device):  # device is a json object
        if (len(device) != SQL_INS_DEVICE_LEN): 
            print ('insertDevice: invalid data')
            return -1
        if (self.debug):
            print (device)    
            print() 
        self.cursor.execute (SQL_INS_DEVICE, self.jsonToDevice(device))
        self.connection.commit()
        return self.cursor.lastrowid
        

    def getDevice (self, mac_id):
        #print ('fetching: {}'.format(mac_id))
        self.cursor.execute (SQL_GET_DEVICE, (mac_id,));     # OBSERVE: (device_id,) has a comma and parenthesis
        rows = self.cursor.fetchone()
        return rows;
        
        
    def removeDevice (self, mac_id):
        if (self.debug):
            print ('deleting device: {}'.format(mac_id))
        self.cursor.execute (SQL_DELETE_DEVICE, (mac_id,));   # OBSERVE: (device_id,) has a comma and parenthesis
        
        
    def getDeviceCount (self):
        self.cursor.execute (SQL_NUM_ROWS_DEVICE); 
        rows = self.cursor.fetchone()
        return rows[0]; 
      
        
    def jsonToDevice (self, jdevice):
        dev_list = []
        for param in device_param_list:        
            if param in jdevice:
                dev_list.append (jdevice[param])    
        str_night_hrs = []
        for nh in jdevice['night_hours']:
            str_night_hrs.append (str(nh))
        dev_list.append (",".join (str_night_hrs))
        str_light_thresh = []
        for lt in jdevice['light_thresholds']:
            str_light_thresh.append(str(lt))
        dev_list.append (",".join (str_light_thresh))
        tup = tuple(dev_list)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup  
#------------------------   
       
    def insertDeviceType (self, device_type):
        if (len(device_type) != SQL_INS_DEVICE_TYPE_LEN): 
            print ('insertDeviceType: invalid data')
            return -1          
        self.cursor.execute (SQL_INS_DEVICE_TYPE, self.jsonToDeviceType(device_type))
        self.connection.commit()
        return self.cursor.lastrowid       
        
        
    def jsonToDeviceType (self, jdevice_type):
        device_type_list = []
        for param in device_type_param_list:        
            if param in jdevice_type:
                device_type_list.append (jdevice_type[param])    
        tup = tuple (device_type_list)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup     
#------------------------   

    def insertDeviceData (self, device_data):
        print ('number of keys in device data: ', len(device_data))
        if (len(device_data) != SQL_INS_DEVICE_DATA_LEN): 
            print ('insertDeviceData: invalid data')
            return -1        
        self.cursor.execute (SQL_INS_DEVICE_DATA, self.jsonToDeviceData(device_data))
        self.connection.commit()
        return self.cursor.lastrowid        
        
        
    def jsonToDeviceData (self, jdevice_data):
        lis = []
        for param in device_data_param_list:        
            if param in jdevice_data:
                lis.append (jdevice_data[param]) 
        if 'data' in jdevice_data:   
            lis.append (json.dumps (jdevice_data['data']))
        tup = tuple (lis)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup           
#------------------------   

    def insertDeviceEvent (self, device_event):
        if (len(device_event) != SQL_INS_DEVICE_EVENT_LEN): 
            print ('insertDeviceEvent: invalid data')
            return -1
        self.cursor.execute (SQL_INS_DEVICE_EVENT, self.jsonToDeviceEvent(device_event))
        self.connection.commit()
        return self.cursor.lastrowid         
        
        
    def jsonToDeviceEvent (self, jdevice_event):
        lis = []
        for param in device_event_param_list:        
            if param in jdevice_event:
                lis.append (jdevice_event[param])    
        tup = tuple (lis)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup                
        
#-----------------------------------------------------------------------------------------------------------------------
# UNIT TESTS
#-----------------------------------------------------------------------------------------------------------------------        

rand_mac = ''.join(random.choice('0123456789ABCDEF') for n in range(10))  # MAC ID has to be unique

def print_time():
    try:
        print("local time:")
        print(db.getTimeStamp ())
    except Exception as e:
        print ('ERROR: ', str(e))  


def create_tables():
    print ('\ncreating tables..')
    i = 0
    try:
        i += 1
        for sql in CREATE_SQLS:
            db.createTable (sql)
            print ("Table {} created.".format(i))                  
    except Exception as e:
        print ('ERROR: ', str(e))  
        

def list_tables():
    print ('\nlist of tables:')
    try:
        rows = db.listTables()  
        for row in rows:
            print (row)    # NOTE: each row is a tuple with a single element                
    except Exception as e:
        print ('ERROR: ', str(e))  
        
             
def remove_table (table_name):
    print ('\nremoving table..')
    try:
        db.removeTableByName (table_name)
        print ("Table {} removed.".format(table_name))
    except Exception as e:
        print ('ERROR: ', str(e))  
            
            
def remove_all_tables():
    print ('\nremoving tables..')
    i = 0
    for sql in DROP_SQLS:
        try:
            i += 1
            db.removeTable (sql)
            print ("Table {} removed.".format(i))              
        except Exception as e:
            print ('ERROR: ', str(e))  
        
        
def add_conf():    
    print ('\nadding config item..')
    try:             
        conf_item = { 
                      'config_id' : 'config_item{}'.format(random.randint(0,1000)), 
                      'config_item' : 'CONFIG_VALUE_vvv012'
                    }
        rownum = db.insertConfig (conf_item)
        print ('row {} inserted.'.format(rownum))
        row_count = db.getConfigRowCount()
        print ('total: {} rows.'.format(row_count))
    except Exception as e:
        print ('ERROR: ', str(e))  
             
             
def print_conf():  
    print ('\nprinting config..')
    try:     
        item_keys = []
        rows = db.getConfig(3)
        for row in rows:
            print (row)
            print (row[0])
            item_keys.append (row[0])
        print ('Table has {} rows.'.format(db.getConfigRowCount()))
        print()
        print (item_keys)
        for key in item_keys:
            item = db.getConfigItem (key)
            print(item)
    except Exception as e:
        print ('ERROR: ', str(e))  
                          
def add_dev():      
    global rand_mac
    print ('\nadding device..')
    rand_mac = ''.join(random.choice('0123456789ABCDEF') for n in range(10))
    print ('Device MAC : {}'.format(rand_mac))
    data = {
        'MAC' : rand_mac,
        'device_name' : 'Bed side light 2',
        'location' : 'bed room',
        'device_type' : 'Relays-8 V3.0',
        'group_id' : 'G1', 
        'primary_relay' : 1,
        'active_low' : 0,
        'status_freq_mins' : 5,
        'auto_off_mins' : 2.5,
        'night_hours' : [18,15,6,0],        
        'light_thresholds' : [80,120,50],
        'enabled' : 1,
        'online' : 1
    }
    #print (data)
    #print ('Number of entries in device json: ', len(data))
    try:
        db.insertDevice (data)
    except Exception as e:
        print ('ERROR: ', str(e))          
   
   
def print_dev():
    print ('\nrecently added device:')
    dev = db.getDevice(rand_mac)   # just created, and globally saved
    print (dev)
    
    
def remove_dev():
    try:
        print ('\nremoving device type..')        
        db.removeDevice (rand_mac)
    except Exception as e:
        print ('ERROR: ', str(e))  

   
def add_devtype():
    try:
        print ('\nadding device type..')    
        dev_type = {
                     'device_type': 'Quad-Relays',  
                     'version': '1.0'
                   }
        rows = db.insertDeviceType (dev_type)
        print ('Rows in deviceType: {}'.format(rows)) 
    except Exception as e:
        print ('ERROR: ', str(e)) 
        
        
def add_devdata():
    try:              
        print ('\nadding device data..')
        dev_status = {
                        "LIGHT" : 352, 
                        "TEMP" : 25.6, 
                        "HUMI" : 89
                     }
        dev_data = {
                      'MAC' : rand_mac, 
                      'time_stamp' : db.getTimeStamp(), 
                      'relay_status' : '0110', 
                      'data' : dev_status     # this will be stringified while inserting
                   } 
        rows = db.insertDeviceData (dev_data)
        print ('Rows in deviceData: {}'.format(rows))
    except Exception as e:
        print ('ERROR: ', str(e)) 
        
        
def add_devevent():
    try:           
        print ('\nadding device event..')
        dev_event = {
                       'MAC' : rand_mac, 
                       'time_stamp' : db.getTimeStamp(), 
                       'event_type' : 'BOOT',
                       'event_body' : 'ESP8266 Restarting..'
                     }
        rows = db.insertDeviceEvent (dev_event)
        print ('Rows in deviceEvent: {}'.format(rows))     
    except Exception as e:
        print ('ERROR: ', str(e)) 
            
#-----------------------------------------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------------------------------------        
            
if __name__ == '__main__':

    db_file_name = r"data\HomeAutomation.db"    #  .\data folder must exist already
    db = HubDB (debug=True)
    
    print ('\nconnecting to DB: ', db_file_name)    
    if db.connect (db_file_name):
        print ('connected.')
    else:
        print ('Invalid connection.')
        sys.exit(0)             
        
    create_tables()
    list_tables()
    
    #remove_table ('config')
    #remove_table ('device')
    #remove_all_tables()
    #list_tables()
    
    add_conf()
    print_conf()
    add_dev()
    print_dev()
    add_devtype()
    add_devdata()
    add_devevent()
    
    if db is not None:
        db.close()             
    print ('Done!')
