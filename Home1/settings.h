// settings.h
#ifndef SETTINGS_H
#define SETTINGS_H

#include "pins.h"

#define  FIRMWARE_VERSION        1            // increment the firmware version for every revision
#define  BAUD_RATE               115200       // serial port

#define  CONFIG_FILE_NAME        "/config.txt"   // SPIFF file; so The leading slash is essential !
#define  CONFIG_FILE_SIZE        500             // bytes; the raw text file on the flash
#define  JSON_CONFIG_FILE_SIZE   700             // bytes; including json overhead: https://arduinojson.org/v6/assistant/

#define  RELAY_ACTIVE_LOW        0            // 1 if relays are active low; 0 for active high 
#define  PRIMARY_RELAY           0            // the main light for automatic control is 0,1,2... NUM_RELAYS
#define  BLINK_COUNT1            4            // device identifier (IFF) blinking
#define  BLINK_COUNT2            8            // device identifier (IFF) blinking

#define  UNIVERSAL_GROUP_ID      "0"          // TODO: use this to listen for pan-group messages
#define  UNIVERSAL_DEVICE_ID     "0"          // all devices in a group listen on this channel

#define  APP_NAME                "Auto Relays"  // this is only for display
#define  APP_ID                  "home"       //  max: MAX_TINY_STRING_LENGTH 
#define  ORG_ID                  "intof"      //  max: MAX_TINY_STRING_LENGTH 
#define  GROUP_ID                "G0"         // test group; to be overriden by config.txt file in Flash 
#define  HUB_ID                  "HUB1"       // max: MAX_TINY_STRING_LENGTH 

#define  NIGHT_START_HOUR        18           // 6.00 PM to 6.30 AM is considered night (for winter)
#define  NIGHT_END_HOUR          6
#define  NIGHT_START_MINUTE      0      
#define  NIGHT_END_MINUTE        30

#define  DAY_LIGHT_THRESHOLD     300
#define  NIGHT_LIGHT_THRESHOLD   100

#define  STATUS_FREQUENCEY       5            // in minutes
#define  AUTO_OFF_TIME_MIN       1.5          // in minutes 

#endif
