# SQLite wrapper class
# https://www.sqlitetutorial.net/sqlite-python/insert/
# > sqlite3 data\HomeAutomation.db
# > select * from config;
# > .quit
# NOTE: SQLite does not enforce the data type of values you put into columns. So you can put text into a numeric field, for eg.
'''
If you get the error:
self.cursor.execute (SQL_GET_CONFIG, (num_rows)); ValueError: parameters are of unsupported type
Remember you have to pass a tuple as parameter to the query. A tuple must have parantheses and a comma.
'''

import json
import sqlite3
import random
from sqlite3 import Error


SQL_INS_CONFIG = '''INSERT INTO  config 
          (config_id, config_item)
          VALUES (?,?);'''
SQL_INS_CONFIG_LEN = 2
SQL_GET_CONFIG = 'SELECT * FROM config  limit ?;'
SQL_GET_CONFIG_ITEM = 'select * from config where config_id=?'
SQL_NUM_ROWS_CONFIG = 'select count (*) from config;'

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
         
SQL_INS_DEVICE_TYPE = '''INSERT INTO  deviceType 
          (device_type, version) 
          VALUES (?,?);'''
SQL_INS_DEVICE_TYPE_LEN = 2
              
SQL_INS_DEVICE_DATA = '''INSERT INTO  deviceData
          (MAC, time_stamp, relay_status, data) 
          VALUES (?,?,?,?);''' 
SQL_INS_DEVICE_DATA_LEN = 4 
    
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
    device_param_list = [    # Do NOT change this order!
    'MAC', 'device_name',  'location', 'device_type',
    'group_id',   'primary_relay',  'active_low',
    'status_freq_mins',  'auto_off_mins', 'enabled', 'online'
    ]  # there are two more; they are array types
  
    #  if file name is ":memory:" it is created in RAM    
    def __init__(self, debug=False):   
        self.debug = debug
                
                
    def connect (self, db_file_name=":memory:"):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connection = sqlite3.connect (db_file_name)
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
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_GET_TIMESTAMP);
        ts = self.cursor.fetchone()[0]
        if (self.debug):
            print (ts)    
        return (ts)
#------------------------  

    def insertConfig (self, config):
        if (len(config) != SQL_INS_CONFIG_LEN): 
            print ('insertConfig: invalid data')
            return -1
        if (self.debug):
            print (config)               
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_INS_CONFIG, config)  # TODO: catching exception will impact performance?
        self.connection.commit()
        return self.cursor.lastrowid
        
        
    def getConfig (self, num_rows=1):
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_GET_CONFIG, (num_rows,)); # NOTE: (num_rows,) has a tuple syntax
        rows = self.cursor.fetchall()
        return rows;
        

    def getConfigItem (self, item_id):
        #print ('fetching: {}'.format(item_id))
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_GET_CONFIG_ITEM, (item_id,)); # OBSERVE: the comma and parenthesis in (item_id,) 
        rows = self.cursor.fetchall()
        return rows[0];
        
        
    def getConfigRowCount (self):
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_NUM_ROWS_CONFIG); 
        rows = self.cursor.fetchall()
        return rows[0][0];        
#------------------------            
            
    def insertDevice (self, device):
        if (len(device) != SQL_INS_DEVICE_LEN): 
            print ('insertDevice: invalid data')
            return -1
        if (self.debug):
            print (device)     
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_INS_DEVICE, device)  # TODO: catching exception will impact performance?
        self.connection.commit()
        return self.cursor.lastrowid
        

    def getDevice (self, mac_id):
        #print ('fetching: {}'.format(mac_id))
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_GET_DEVICE, (mac_id,)); # OBSERVE: (device_id,) has a comma and parenthesis
        rows = self.cursor.fetchall()
        return rows[0];
        
        
    def getDeviceCount (self):
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_NUM_ROWS_DEVICE); 
        rows = self.cursor.fetchall()
        return rows[0][0]; 
      
        
    def jsonToDevice (self, jdevice):
        dev_list = []
        for param in self.device_param_list:        
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
        if len(dev_list) != SQL_INS_DEVICE_LEN :
            print ('Invalid device JSON (length must be {})'.format(SQL_INS_DEVICE_LEN))
            return None
        tup = tuple(dev_list)  # this is a deep copy  
        if self.debug:
            print (tup)
        return tup  
#------------------------   
       
    def insertDeviceType (self, device_type):
        if (len(device_type) != SQL_INS_DEVICE_TYPE_LEN): 
            print ('insertDeviceType: invalid data')
            return -1
        if self.debug:
            print (device_type)            
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_INS_DEVICE_TYPE, device_type)  # TODO: catching exception will impact performance?
        self.connection.commit()
        return self.cursor.lastrowid       
        

    def insertDeviceData (self, device_data):
        if (len(device_data) != SQL_INS_DEVICE_DATA_LEN): 
            print ('insertDeviceData: invalid data')
            return -1
        if self.debug:
            print (device_data)            
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_INS_DEVICE_DATA, device_data)  # TODO: catching exception will impact performance?
        self.connection.commit()
        return self.cursor.lastrowid        
        

    def insertDeviceEvent (self, device_event):
        if (len(device_event) != SQL_INS_DEVICE_EVENT_LEN): 
            print ('insertDeviceEvent: invalid data')
            return -1
        if self.debug:
            print (device_event)            
        #cur = self.connection.cursor()
        self.cursor.execute (SQL_INS_DEVICE_EVENT, device_event)  # TODO: catching exception will impact performance?
        self.connection.commit()
        return self.cursor.lastrowid                
#-------------------------------------------------------------------------------
        
        
if __name__ == '__main__':

    db_file_name = r"data\HomeAutomation.db"    #  .\data folder must exist already
    db = HubDB (debug=True)
    if not db.connect (db_file_name):
        print ('Invalid connection.')    
    else:
        print("local time:")
        print(db.getTimeStamp ())
        
        conf_item = ("config_item{}".format(random.randint(0,1000)), "CONFIG_VALUE_vvv012")
        rownum = db.insertConfig (conf_item)
        print ('row {} inserted.'.format(rownum))
        row_count = db.getConfigRowCount()
        print ('total: {} rows.'.format(row_count))
                
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
        print (data)
        print()
        tupdevice = db.jsonToDevice(data) 
        db.insertDevice (tupdevice)
        
        dev_type = ('Quad-Relays', '1.0')
        rows = db.insertDeviceType (dev_type)
        print ('Rows in deviceType: {}'.format(rows)) 
      
        dev_data = (rand_mac, db.getTimeStamp(), '0110', '{"LIGHT" : 352, "TEMP" : 25.6, "HUMI" : 89}') 
        rows = db.insertDeviceData (dev_data)
        print ('Rows in deviceData: {}'.format(rows))
        
        dev_event = (rand_mac, db.getTimeStamp(), 'BOOT', 'ESP8266 Restarting..') 
        rows = db.insertDeviceEvent (dev_event)
        print ('Rows in deviceEvent: {}'.format(rows))
                
        db.close()         
      
    print ('Done!')
     