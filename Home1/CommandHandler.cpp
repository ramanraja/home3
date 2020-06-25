// CommandHandler.cpp
 
#include "CommandHandler.h" 
#include "hardware.h"

const char* modes[] = {"AUTO", "MANUAL"};  // NOTE: boolean manual_override is used as index into this array

// external callback functions defined in main .ino file 
void reset_wifi();
void check_for_updates();
bool is_night_time(); // this gets the cached value in main .ino

/**
#ifndef PORTICO_VERSION 
  bool is_occupied();
#endif
**/

CommandHandler::CommandHandler() {
}
 
void CommandHandler::init(Config *pconfig, MqttLite *pclient, Hardware *phardware) {
    pC = pconfig;
    pClient = pclient;
    pHard = phardware;
}
 
// Takes the global status message and publishes it
// NOTE: You MUST set up the status_message before calling this !
void CommandHandler::publish_message () {
    status_msg[MAX_MSG_LENGTH-1] = '\0';  // for safety, in case our snprintf() overflowed
    //SERIAL_PRINT(F("Publishing: "));
    //SERIAL_PRINTLN(status_msg);
    pClient->publish(status_msg);
}

void CommandHandler::send_not_implemented () {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"NOT_IMPLEMENTED\"}");
    publish_message();
}    

// TODO: In the following two cases, add additional overloaded methods: they should
// take the status or data as function arguments (push model)
void CommandHandler::send_status () {  
    // this is pull model; in response to an MQTT command
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"S\":\"%s\"}", pHard->get_relay_status());    
    publish_message();
}

// sends an outgoing message to Hub to get the time; asynchronous request.
void CommandHandler::request_time() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"R\":\"TIME\"}");    
    publish_message();
}

void CommandHandler::send_data () { // TODO: take the status as an argument?
    if (data_paused) {
        send_paused_msg();
        return; 
    }
    // this is pull model; in response to an MQTT command; gets the last known values (not current)
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"D\":{\"S\":\"%s\", \"L\":%d}}", pHard->get_relay_status(), pHard->get_light_level());    
    publish_message();
}

void CommandHandler::get_param(const char* param) {
     snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"P\":\"%s=%s\"}", param, pC->get_param(param)); 
     publish_message();
}

void CommandHandler::send_paused_msg() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"I\":\"DATA_PAUSED\"}");    
    publish_message();  
}

void CommandHandler::send_version() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"V\":\"%d\"}", FIRMWARE_VERSION);    
    publish_message();
}

// Send MAC address - This is useful for polling the devices on the broadcast topic
void CommandHandler::send_mac_address() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"M\":\"%s\"}", pC->mac_address);    
    publish_message();
}

void CommandHandler::send_heap() {
    long heap = ESP.getFreeHeap();
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"H\":\"%ld\"}", heap);    
    publish_message();
}

void CommandHandler::send_org() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"O\":\"%s\"}", pC->org_id);    
    publish_message();
}

void CommandHandler::send_group() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"G\":\"%s\"}", pC->group_id);    
    publish_message();
}

// a command was received to put the device in auto mode
// "A" tag stands for both auto/manual mode
void CommandHandler::auto_mode () {
    manual_override = false;  // this puts the device in auto mode
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"A\":\"%s\"}", modes[0]); // 0=auto, 1=manual   
    publish_message();
}

// a command was received to put the device in manual mode
// "A" tag stands for both auto/manual mode
void CommandHandler::manual_mode () {
    manual_override = true;  // this puts the device in manual mode
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"A\":\"%s\"}", modes[1]); // 0=auto, 1=manual   
    publish_message();
}

// Logging values ("L") are responses to queries received
// To check whether we are following active low or active high
void CommandHandler::send_active_onoff() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"ON=%d, OFF=%d\"}", pC->ON,pC->OFF);    
    publish_message();
}

void CommandHandler::send_is_night() {
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"IS_NIGHT=%d\"}", is_night_time());    
    publish_message();
}

// invalid command
void CommandHandler::send_error() { 
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"CMD_ERROR\"}");    
    publish_message();
}

// a request was received to intimate the current mode; this is the reply
void CommandHandler::send_mode() {
    byte m = (byte)manual_override;  // 0=auto, 1=manual
    SERIAL_PRINT(F("Control Mode: "));
    SERIAL_PRINTLN (modes[m]);
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"MODE=%s\"}", modes[m]);    
    publish_message();
}

void CommandHandler::send_is_occupied() {  // TODO: decide how to use this
    SERIAL_PRINTLN(F("is_occupied flag is not valid for Relay Controller"));  
    send_not_implemented(); 
}
 
// This rebooting happens in response to a remote MQTT command to restart.
// (Autonomous rebooting will go under "B" tag).
void CommandHandler::reboot() {
    print_heap();  
    snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"L\":\"%s\"}", "Device is rebooting !");    
    publish_message();
    pHard->reboot_esp();
}

// Downloads config.txt file. If successful, restarts the device
void CommandHandler::download_config(){
    print_heap();
    int result = pC->download_config();
    print_heap();
    if (result==CODE_OK) {
        snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"I\":\"%s\"}", "Config file updated.");  
        publish_message();
        SERIAL_PRINTLN(F("[Config] Restarting ESP..."));
        yield();
        delay(2000);
        ESP.restart();
    } else {
        snprintf (status_msg, MAX_MSG_LENGTH-1, "{\"I\":\"%s%s\"}", "Failed to download config file: ", pC->get_error_message(result));  
        publish_message();      
    }
} 
//--------------------------------------------------------------------------------------

#define  NUM_COMMANDS    21  // excluding on and off commands; index runs from 0 to NUM_COMMANDS-1
// NOTE: If you change the order of the following strings, you must change the switch cases also !
const char* commands[] = { "STA", "VER", "MAC", "GRO", "ORG", "HEA", "REB", "DEL", "UPD", "AUT", 
                           "MAN", "MOD", "BL0", "BL1", "DAT", "CER", "LOJ", "ISN", "OCC", "PAU", "RES" };

void CommandHandler::handle_command(const char* command_string) {
    if (strlen (command_string) < 3) {
        SERIAL_PRINTLN(F("Command can be: STA,UPD,VER,MAC,HEA,DEL,GRO,ORG,RES,ONx,OFx etc"));
        return;
    }
    // ON commands: ON0, ON1 etc
    if (command_string[0]=='O' && command_string[1]=='N') { 
        if (command_string[2] < '0' ||  command_string[2] >= NUM_RELAYS+'0') 
            SERIAL_PRINTLN(F("-- Error: Invalid relay number --"));
        else
            pHard->relay_on(command_string[2] - '0'); // this sends the status also 
        print_heap();
        return;
    }
    // OFF commands: OF0, OF1 etc.
    if (command_string[0]=='O' && command_string[1]=='F') { 
        if (command_string[2] < '0' ||  command_string[2] >= NUM_RELAYS+'0') 
            SERIAL_PRINTLN(F("-- Error: Invalid relay number --"));
        else
            pHard->relay_off(command_string[2] - '0'); // this sends the status also 
        print_heap();
        return;
    }
    int command_index = -1;
    for (int i=0; i<NUM_COMMANDS; i++) {
        if (strcmp(command_string, commands[i]) == 0) {
            command_index = i;
            break;
        }
    }
    if (command_index < 0) { // received cmd is out of syllabus
       SERIAL_PRINTLN(F("-- Error: Invalid command --"));
       send_error();
       print_heap();
       return;
    }
    switch (command_index) {
        case 0: // STA
            send_status();
            break;
        case 1: // VER
            send_version();
            break;
        case 2: // MAC
            send_mac_address();
            break;     
        case 3:  // GRO
            send_group();
            break;
        case 4: // ORG
            send_org();
            break;
        case 5:  // HEA
            send_heap();
            break;   
        case 6:  // REB
            reboot();
            break;
        case 7:  // DEL
            reset_wifi();  // TODO: decide how to use this
            break;
        case 8:  // UPD
            check_for_updates();
            break;     
        case 9:  // AUT
            auto_mode();
            break;
        case 10: // MAN
            manual_mode();
            break;                
        case 11: // MOD
            send_mode();
            break;               
        case 12: // BL0
            pHard->blink_led(BLINK_COUNT1);
            break;                
        case 13: // BL1
            pHard->blink_led(BLINK_COUNT2);
            break;       
        case 14: // DAT
            send_data(); // on-demand data
            break;            
        case 15: // CER
            download_config(); // download config.txt file in SPIFF
            break;                        
        case 16: // LOJ = on/off logic levels
            send_active_onoff();
            break;
        case 17: // ISN
            send_is_night();
            break;
        case 18: // OCC
            send_is_occupied(); // TODO: this is redundant 
            break;
        case 19: // PAU        
            SERIAL_PRINTLN(F("Data paused"));    
            data_paused = true;
            break;
        case 20: // RES           
            SERIAL_PRINTLN(F("Resuming data")); 
            data_paused = false;
            break;            
        default :
            SERIAL_PRINTLN(F("-- Error: Invalid command index --")); // signals an implementation bug
            send_error();
            break;                              
    }
    print_heap();
}





 
