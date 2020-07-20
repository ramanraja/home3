// home automation controller
// This is the portico controller version :  intof/home/status/G0/2CF432173BC0
// code is cloned from IoTRelay2.ino
// New: implemented auto on/off at dawn/dusk  
/***
This is the new portico controller fixed outside the grill door on 26-June-2020
 Operates 2 IoT relays through an MQTT broker on the local Wifi network.
 These relays are active LOW. Set this in config.txt ***
 Uses Vaidy's round PCB with 2 relays, LDR, PIR and Radar
 pub topic: intof/home/status/G0/2CF432173BC0

Changes for this particular board:

Flash: NodeMCU 4 MB/ 2MB/ 1019KB

settings.h : 
#define  RELAY_ACTIVE_LOW        1       
#define  PRIMARY_RELAY           1    
#define  APP_NAME                "Portico Lights"  
(NOTE: APP_ID is still retained as 'home')
#define  PRIMARY_LIGHT_CORRECTION    80  

conf_home.txt: 
"ACTIVE_LOW":1,
"PRIMARY_REL":1,
"DAY_LIGHT": 130,
"NIGHT_LIGHT":80,
"LIGHT_CORRECTION" : 80

pins.h : 
#define LDR_PRESENT

#define RELAY1     5      // D1 
#define RELAY2     4      // D2 
#define RELAY3     5      // D1
#define RELAY4     4      // D2

#define LED        3      // Rx  
****/