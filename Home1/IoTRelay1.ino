// LED blinking logic indicate wifi/mqtt status
// check all PubSubClient error messages and print the return code
// test it with 2 relays or 8 relays (check panic if 9th relay is added)
// implement set param command
// implement 2 falavours of is_night properly, and cache the value in main.ino
// implement sync_time() and set_time() etc with backup dead reckoning
// implement auto on/off at night time
// if wifi or hub/mqtt broker fails: implement retry logic
// make use of persistent messages, QOS=1, sticky subscriptions and longer socket time out (existing: 15 sec)

/*
 Operates 4 IoT relays through an MQTT broker on the local Wifi network.
 
 Rhydo Labz 8266 IoT relay boards
 https://www.rhydolabz.com/wiki/?p=19640
 https://www.rhydolabz.com/wiki/?p=19617
 https://www.rhydolabz.com/wiki/wp-content/uploads/SCH-3038.pdf
 
 Rydolabz IOT WIFI BOARD with SMPS & SSR 4 relays AND 2 INPUTS version
 has 4 solid state relays connected to GPIO 13,12,14,16.
 The 2 electro mechanical relays version has the relays at GPIO 13,12.
  
 ESP07 (generic 8266) with 1 MB. It has a blue LED on GPIO 2.
 Two 220 Ohm opto coupler 'digital' inputs at GPIO 5, 4.
 ADC input - MAX 3.3 V input, as it uses an internal divider.
 GPIO 0 is available at Jumper J1. (To drive an LED from GPIO0, use 1K resistor). 
  
 To upload code, put the jumper J1 (GPIO 0) in place and press the reset button.
 To run the code, remove jumper J1 and press Reset. 
*/

#include "main.h"

// helper classes
Timer T;
Config C;
MyFi W;
Hardware hard;
MqttLite mqtt;
CommandHandler cmd;
OtaHelper ota; // TODO: create this only when needed ?

void setup() {
    hard.init_serial(); // this is almost like a static method, so OK to call before hard.init()
    C.init();  
    C.dump(); // this needs init_serial
    hard.init(&C, &T, &cmd); // this needs properly initialized C.active_low
    // buy some time blinking the LED; the wifi can connect during that time.
    hard.blink0();
    bool wifi_ok = W.init (&C);
    bool mqtt_ok = mqtt.init (&C, &W);
    cmd.init (&C, &mqtt, &hard);
    ota.init (&C, &mqtt);
    if (!wifi_ok)  // total communication failure
          hard.blink3();  // rapid blinks
    else {
          if (!mqtt_ok) // MQTT failed, but wifi is OK
               hard.blink2();  // fast blinks   
          else  // all is well
               hard.blink1();  // slow blinks
    }
    //T.every(C.tick_interval, tick); // TODO: implement this, if neessary
    T.every(3000, tick);
    T.every(C.sensor_interval, one_minute_logic);  // TODO: implement this
}

void loop() {
    T.update();
    if (W.update())
        mqtt.update();
}

int count = 0;
void tick() {  // TODO: implement this, if needed
    SERIAL_PRINT ("*");
    count++;
    if (count==10) {
        count = 0;
        SERIAL_PRINTLN("\n");
    }
}

// one_minute_logic() is called every 1 minute by the Timer
// Contacts Time Server once in 5 minutes,  and stores it in cache
void one_minute_logic() {  // TODO: implement this

    SERIAL_PRINTLN ("~ ONE_MINUTE_LOGIC ~");
    print_heap();
    /***
    bool time_for_status = hard.read_sensors(); //<- this returns true if it is time to send a status report, ie, 5 minutes elapsed
    if (!time_for_status)
        return;
    if (comm_status == COMM_OK) {  // if AWS and time server were properly initialized at the beginning
        check_day_or_night (false);  // this stores it in global variable is_night
    #ifndef PORTICO_VERSION 
        handle_transition();  // handle that one special case of day break
    #endif
        cmd.send_data();  // NOTE: pubsubclient.reconnect() is regulary called in aws.update()
    } else {    // status is COMM_BROKEN
        check_day_or_night (true);  // fall back on light based determination
        repair_comm();    // this is to repair AWS initialization failure in init_cloud() at the beginning 
    }
    ***/
}

// MQTT subscribed message arrived
// NOTE: the incoming command from the hub is a simple text command; it is not Json formatted.
// Leading special characters like +,- and # are used when the command needs parsing
void  app_callback (const char* command_string) {
    SERIAL_PRINTLN (command_string); 
    if (command_string[0] == '-') {
        SERIAL_PRINT (F("GET PARAM request: "));
        SERIAL_PRINTLN ((char*)(command_string+1));
        cmd.get_param ((char*)(command_string+1)); // TODO: this runs on the MQTT thread; move this to the main loop 
    }
    else if (command_string[0] == '+') {
        SERIAL_PRINT (F("SET PARAM request: "));
        SERIAL_PRINTLN ((char*)(command_string+1)); // TODO: split it into name,value pair using space as delimiter
        SERIAL_PRINTLN (F("\n<<<--- THIS IS set-param STUB --->>>\n"));   // TODO: implement
        set_param ("par", "val");
    }    
    else if (command_string[0] == '#') {
        SERIAL_PRINT (F("Time server notice: "));
        SERIAL_PRINTLN ((char*)(command_string+1)); // TODO: split it into hour,min pair using space as delimiter
        SERIAL_PRINTLN (F("\n<<<--- THIS IS time STUB --->>>\n"));   // TODO: implement
        // C.set_time (hour, min);  
    }      
    else
        cmd.handle_command (command_string); // TODO: this runs on the MQTT thread; move this to the main loop
}

void check_for_updates() {
    SERIAL_PRINTLN(F("---Firmware update command received---"));
    ota.check_and_update();
    SERIAL_PRINTLN(F("Reached after OTA-check for updates.")); // reached if the update fails
}

short is_night_time() {   // cache it
    bool is_nite = C.is_night_time();  // TODO: move this to hardware.cpp ? cache it in main? dead reckoning?
    if (is_nite == TIME_UNKNOWN)
    is_nite = hard.is_night_time();
    return (is_nite);
}

void set_param (const char* param, const char *value) {  // TODO: implement this
   /***
    bool result = C.set_param(param, value); // this returns true if there was an error
    if (result) {
        SERIAL_PRINTLN (F("--- SET Failed ---"));
        pClient->publish(C.mqtt_pub_topic, "{\"I\":\"SET-ERROR\"}");
    }
    else {
        SERIAL_PRINTLN (F("SET: OK"));
        pClient->publish(C.mqtt_pub_topic, "{\"C\":\"SET-OK\"}");    
    }
    ***/
   cmd.send_not_implemented();
}

void reset_wifi() {
    SERIAL_PRINTLN (F("\n<<<--- Erase Wifi: This is a stub \n--->>>"));
    /**
    SERIAL_PRINTLN(F("\n*** ERASING ALL WI-FI CREDENTIALS ! ***"));   
    SERIAL_PRINTLN(F("You must configure WiFi after restarting"));
    pClient->publish(C.mqtt_pub_topic, "{\"I\":\"Erasing all WiFi credentials !\"}");
    delay(500);
    pClient->publish(C.mqtt_pub_topic, "{\"C\":\"Configure WiFi after restarting\"}");  
    myfi.erase_wifi_credentials(true); // true = reboot ESP
    ***/
}
