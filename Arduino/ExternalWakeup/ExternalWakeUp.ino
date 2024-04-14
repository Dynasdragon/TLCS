#include "esp_camera.h"
#include "Arduino.h"
#include "FS.h"                // SD Card ESP32
#include "SD_MMC.h"            // SD Card ESP32
#include "soc/soc.h"           // Disable brownour problems
#include "soc/rtc_cntl_reg.h"  // Disable brownour problems
#include "driver/rtc_io.h"
#include <EEPROM.h>            // read and write from flash memory
#include "SPIFFS.h"
#include <WiFi.h>

#define CAMERA_MODEL_WROVER_KIT
#include "camera_pins.h"
/*
Deep Sleep with External Wake Up
=====================================
This code displays how to use deep sleep with
an external trigger as a wake up source and how
to store data in RTC memory to use it over reboots

This code is under Public Domain License.

Hardware Connections
======================
Push Button to GPIO 33 pulled down with a 10K Ohm
resistor

NOTE:
======
Only RTC IO can be used as a source for external wake
source. They are pins: 0,2,4,12-15,25-27,32-39.

*/
// define the number of bytes you want to access
#define EEPROM_SIZE 1

// Pin definition for CAMERA_MODEL_AI_THINKER
// #define PWDN_GPIO_NUM     32
// #define RESET_GPIO_NUM    -1
// #define XCLK_GPIO_NUM     21
// #define SIOD_GPIO_NUM     26
// #define SIOC_GPIO_NUM     27

// #define Y9_GPIO_NUM       35
// #define Y8_GPIO_NUM       34
// #define Y7_GPIO_NUM       39
// #define Y6_GPIO_NUM       36
// #define Y5_GPIO_NUM       19
// #define Y4_GPIO_NUM       18
// #define Y3_GPIO_NUM       5
// #define Y2_GPIO_NUM       4
// #define VSYNC_GPIO_NUM    25
// #define HREF_GPIO_NUM     23
// #define PCLK_GPIO_NUM     22
#define BUTTON_PIN_BITMASK 0x200000000 // 2^33 in hex
//const char* ssid = "marketgang2";
//const char* password = "dynamo81";
const char* ssid = "EDDYS-LAPTOP";
const char* password = "eddyiscool";
//const IPAddress host(172,20,10,2); 
//const IPAddress host (192,168,1,118);
const IPAddress host (10,17,75,129);
int port = 81;
WiFiServer wifiServer(5005);

RTC_DATA_ATTR int bootCount = 0;
#define ackPin 14

/*
Method to print the reason by which ESP32
has been awaken from sleep
*/
bool print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); return true; break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); return true; break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); return true; break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); return true; break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); return true; break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); return false; break;
  }
}

void setup(){
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  esp_sleep_enable_ext0_wakeup(GPIO_NUM_33,1); //1 = High, 0 = Low
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG; 

    pinMode(ackPin, OUTPUT);
    digitalWrite(ackPin, LOW);

  //Print the wakeup reason for ESP32
  bool signalled = print_wakeup_reason();
  if(signalled){

    Serial.println("Boot number: " + String(bootCount));

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
      Serial.println("Failed to mount file system");
      return;
    }
    
    

    if(psramFound()){
      config.frame_size = FRAMESIZE_UXGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;

    
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG; 
    

    if(psramFound()){
      config.frame_size = FRAMESIZE_UXGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.jpeg_quality = 5;
      config.fb_count = 1;
    }
          // Init Camera
      esp_err_t err = esp_camera_init(&config);
      if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
      }

    sensor_t * s = esp_camera_sensor_get();
    // initial sensors are flipped vertically and colors are a bit saturated
    if (s->id.PID == OV3660_PID) {
      s->set_vflip(s, 1); // flip it back
      s->set_brightness(s, 2); // up the brightness just a bit
      s->set_saturation(s, -1); // lower the saturation
      s->set_contrast(s, 1);
    }
      // drop down frame size for higher initial frame rate
    if(config.pixel_format == PIXFORMAT_JPEG){
      s->set_framesize(s, FRAMESIZE_VGA);
    }

    #if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
      s->set_vflip(s, 1);
      s->set_hmirror(s, 1);
    #endif

    #if defined(CAMERA_MODEL_ESP32S3_EYE)
      s->set_vflip(s, 1);
    #endif
        WiFiClient client;

    int i = 0;
    bool connected = false;
    while(connected == false && i <= 5) {
        int attempt = client.connect(host,port);
        if(attempt != 0){
          connected = true;
          break;
        }
        i++;
        delay(1000);
    }
    if(connected == false){
        Serial.println("Connection to host failed");
        Serial.println("Going to sleep now");
        esp_deep_sleep_start();
    }


    Serial.println("Connected to server successful!");
    //Increment boot number and print it every reboot
    ++bootCount;
    digitalWrite(ackPin, HIGH);
    delay(1000);
    digitalWrite(ackPin, LOW);

    // capture camera frame
    camera_fb_t *fb = esp_camera_fb_get();
    if(!fb) {
      Serial.println("Camera capture failed");
        return;
    } else {
        Serial.println("Camera capture successful!");
    }

    const char *data = (const char *)fb->buf;
    // Image metadata.  Yes it should be cleaned up to use printf if the function is available
    Serial.print("Size of image:");
    Serial.println(fb->len);
    Serial.print("Shape->width:");
    Serial.print(fb->width);
    Serial.print("height:");
    Serial.println(fb->height);

    client.print("width:");
    client.print(fb->width);
    client.print("height:");
    client.print(fb->height);
    client.print("series:");
    client.print(bootCount);
    client.print("\r\n");
    // Give the server a chance to receive the information before sending an acknowledgement.
    delay(2000);
    getResponse(client, "ack1");
    Serial.print(data);
    client.write(data, fb->len);
    delay(1000);
    client.print("tx_complete");
    delay(2000);
    esp_camera_fb_return(fb);

    Serial.println("Disconnecting...");
    client.stop();

    delay(2000);
    }
  }

  //Go to sleep now
  Serial.println("Going to sleep now");
  esp_deep_sleep_start();
  Serial.println("This will never be printed");
}

void getResponse(WiFiClient client, String msg) {
  Serial.println("Waiting for Ack");
  byte buffer[8] = { NULL };
  while (client.available() > 0 || buffer[0] == NULL) {
    int len = client.available();
    if (len > 8) len = 4;
    String response = client.readString();
    if(response.indexOf(msg) != -1){
      Serial.println("Got Ack");
      break;
    }
  }
}

void loop(){
  //This is not going to be called
}
