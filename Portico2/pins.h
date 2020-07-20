// pins.h

#ifndef PINS_H
#define PINS_H

#include "common.h"

// The maximum number of relays a board can theoretically have is limited to 8 (MAX_RELAYS in common.h)
// The actually present number can be 1 to 8, which is given by NUM_RELAYS  
// Assumption: there will not be more than 8 relays
// Command handler can only handle commands like ON0 to ON9, so the relay count has to be single digit ***
// This is OK, since 8266 has only a limited number of I/O pins

#define HARDWARE_TYPE   "REL4-LDR.1"

// for the RhydoLabz IoT relay board:   
#define NUM_RELAYS      4

// comment out if you do not have a light sensor:
#define LDR_PRESENT
     
#define RELAY1     5      // D1 
#define RELAY2     4      // D2 
#define RELAY3     5      // D1
#define RELAY4     4      // D2

#define BUTTON1    5       // D
#define BUTTON2    4       // D  

#define LDR        A0 
 
#define LED   3              // D9 = Rx pin;  NOTE: you cannot receive any serial port messages (ESP will crash)
///#define LED        2      // D4; built into the board

#define LED_ON     LOW    // assuming active LOW led
#define LED_OFF    HIGH
  
#endif
