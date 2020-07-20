// home automation controller
// TODO:
// Test LED blinking for wifi failuare,MQTT failure
// implement comm_status and repair_comm()
// when there is comm_failure, keep blinking the LED (with siren-like PWM feasible?)
// read light level (unblock the LDRs physically)
// Connect an external LED for Rhydo-Labz boards
// check all PubSubClient error messages and print the return code
// test it with 2 relays or 8 relays (check panic if 9th relay is added)
// implement set param command 
// implement reset_wifi_password
// if wifi or hub/mqtt broker fails: implement retry logic
// Make night start/end times more flexible; remove the constraint that end_time > start_time 
// TODO: ability to add multiple on/off schedules in a day
// A button on hub and a button on the device, to register (when pressed almost simultaneously)
// make use of persistent messages, QOS=1, sticky subscriptions and longer socket time out (existing: 15 sec)

/*
 Operates 4 IoT relays through an MQTT broker on the local Wifi network.
 *** NOTE: Choose Generic 8266/ 1 MB/64 K FS/470K OTA on the IDe; otherwise OTA will fail without any indication! ***
(On the OTA server you will get an exception:
ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host)  
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
    SERIAL_PRINTLN(F("OTA initialized."));
    if (!wifi_ok)  // total communication failure
          hard.blink3();  // rapid blinks
    else {
          if (!mqtt_ok) // MQTT failed, but wifi is OK
               hard.blink2();  // fast blinks   
          else  // all is well
               hard.blink1();  // slow blinks
    }
    SERIAL_PRINTLN(F("sending boot msg.."));
    cmd.send_booting_msg();
    SERIAL_PRINTLN(F("sent boot msg."));
    delay(1000);
    cmd.request_time(); // priming read
    delay(1000);
    yield();
    SERIAL_PRINTLN(F("Priming:Check day or night.."));
    check_day_or_night();  // this sets is_night flag
    operate_relays();   // this uses is_night flag
    SERIAL_PRINTLN(F("Setting up timers.."));
    //T.every(C.tick_interval, tick); // TODO: implement this, if neessary
    T.every(60000, one_minute_logic);  // This is hard coded because dead reckoning needs exactly 1 minute increments
}

void loop() {
    T.update();
    if (W.update())
        mqtt.update();
}

// one_minute_logic() is called every 1 minute by the Timer
// Counts upto,say, 5 and then triggers five_minute_logic()
short minute_count = 0;   // counts from 0 to 5 and resets
void one_minute_logic() {  
    //print_heap();
    C.increment_clock(); // dead reckoning
    check_day_or_night(); // this merely sets the global variable is_night 
    hard.read_sensors();
    minute_count++;
    if (minute_count < C.status_report_frequency) // usually 5 minutes
        return;
    minute_count = 0;    
    five_minute_logic();
}

void five_minute_logic() {   // ie,usually 5 minutes!
    cmd.request_time();
    if (C.auto_dawn_dusk_mode && !cmd.manual_override)
        operate_relays();         // if is_night==true, operate the primary relay & vice-versa
    hard.prepare_status_data();   // compute the average readings
    cmd.send_data();  
    repair_comm(); 
    print_heap();
}

short is_night = TIME_UNKNOWN;
short was_night = TIME_UNKNOWN;   // the previous state

void check_day_or_night () {       // updates the global variable is_night
    is_night = C.is_night_time();   
    if (is_night == TIME_UNKNOWN)   // get a second opinion
        is_night = hard.is_night_time();  // this can also be TIME_UNKNOWN
    if (is_night == TIME_NIGHT && was_night == TIME_DAY)
        handle_dusk_transition();  // day->night
    else
    if (is_night == TIME_DAY && was_night == TIME_NIGHT)
        handle_dawn_transition();  // night->day
    was_night = is_night;
}

// you must have called check_day_or_night() once before this
short is_night_time() {   // respond to query from remote
    return (is_night);
}

// you must call check_day_or_night() before this
void operate_relays() {
    if (is_night == TIME_NIGHT)
        hard.primary_light_on();
    else if (is_night == TIME_DAY)
        hard.primary_light_off();
    // otherwise (TIME_UNKNOWN), maintain status quo
}

void handle_dawn_transition() {
    SERIAL_PRINTLN (F("Good Morning!"));   
    /***
    if (occupied && !cmd.manual_override) {  
        occupied = false;
        hard.primary_light_off();
    }    
    ***/
    if (!cmd.manual_override) {
        hard.primary_light_off();
        cmd.send_status();
    }
}

void handle_dusk_transition() {
    SERIAL_PRINTLN (F("Good Night!"));    
    if (!cmd.manual_override) {
        hard.primary_light_on();
        cmd.send_status();
    }
}

bool repair_comm() {
  SERIAL_PRINTLN (F("\nREPAIR COMM STUB\n"));   // TODO: implement this
}

// MQTT subscribed message arrived
// NOTE: the incoming command from the hub is a simple text command; it is not Json formatted.
// Leading special characters like +,- and # are used when the command needs parsing
char time_str[3];
short hour, minute;
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
        SERIAL_PRINTLN (F("\n<<<--- THIS IS set-param STUB --->>>\n"));   // TODO: implement all params
        set_param ("par", "val");
    }   
    else if (command_string[0] == '#') {  // TODO: move it to +TIM
        SERIAL_PRINT (F("Time server notice: "));
        SERIAL_PRINTLN ((char*)(command_string+1)); 
        // The command string format is "#06:20"
        // TODO: make this more mature!
        if ((char)(command_string[3]) != ':') {
            SERIAL_PRINT (F("\n--- INVALID TIME ---\n"));
            return;
        }        
        time_str[0] = (char)(command_string[1]);
        time_str[1] = (char)(command_string[2]);
        time_str[2] = '\0';
        hour = atoi(time_str);
        time_str[0] = (char)(command_string[4]);
        time_str[1] = (char)(command_string[5]);
        time_str[2] = '\0';
        minute = atoi(time_str);
        if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
            SERIAL_PRINT (F("\n--- INVALID TIME ---\n"));
            cmd.send_error(); 
            return;
        }
        C.set_time (hour, minute);  
        cmd.send_current_time();
    }      
    else
        cmd.handle_command (command_string); // TODO: this runs on the MQTT thread; move this to the main loop
}

void check_for_updates() {
    SERIAL_PRINTLN(F("---Firmware update command received---"));
    ota.check_and_update();
    SERIAL_PRINTLN(F("Reached after OTA-check for updates.")); // reached if the update fails
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
