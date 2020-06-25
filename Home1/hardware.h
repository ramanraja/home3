// hardware.h

#ifndef HARDWARE_H
#define HARDWARE_H

#include "common.h"
#include "pins.h"
#include "config.h"
#include "settings.h"
#include "utilities.h"
#include <Timer.h>    // https://github.com/JChristensen/Timer

#define  MAX_LIGHT        1024   // NodeMCU has 10 bit ADC
#define  NOISE_THRESHOLD  10    // when the light sensor fails, this will be the max ADC noise

class CommandHandler; // forward declaration

class Hardware {
public:
    Hardware ();
    void  init (Config *configptr, Timer *timerptr, CommandHandler *cmdptr);
    void  init_serial();
    bool  metronome();   // call this every minute from Timer
    void  operate_all_relays();  // use this sparingly, if at all!  
    void  release_all_relays();    
    void  relay_on  (short relay_number);
    void  relay_off (short relay_number);
    void  primary_light_on ();
    void  primary_light_off ();
    void  blink0 ();
    void  blink1 ();
    void  blink2 ();
    void  blink3 ();
    void  blink_led (byte times);
    void  led_on ();
    void  led_off (); 
    void  set_led (bool is_on);
    void  print_data ();
    void  print_configuration();
    short is_night_time();     
    int   get_light_level ();
    const char* get_relay_status ();
    void  reboot_esp ();
    void  infinite_loop();
                
private:
    Timer  *pT;
    Config *pC;
    CommandHandler *pCmd;   
    int     sensor_reading_count = 0;
    byte    relay_pin [NUM_RELAYS]  = {RELAY1, RELAY2, RELAY3, RELAY4};    // TODO: rectify this problem!
    byte    led = LED;
    bool    relay_status[NUM_RELAYS];   
    char    relay_status_str[NUM_RELAYS+1];   
    int     analog_reading = 0;  // raw value from the LDR        
    int     light_level = 0;     
    void    read_light();
    void    init_hardware();  
    void    read_sensors();
    void    prepare_status_data();
};


#endif
