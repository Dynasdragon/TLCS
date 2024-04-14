#include "Adafruit_VL53L0X.h"

Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox3 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox4 = Adafruit_VL53L0X();

lox1.setAddress(0x29);
lox2.setAddress(0x30);
lox3.setAddress(0x31);
lox4.setAddress(0x32);

int distance1;
int distance2;
int distance3;
int distance4;
double speed1;
double speed2;
double speed3;
double speed4;

bool speedViolation = false;
bool lightViolation = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  Serial.println("Adafruit VL53L0X test");

  if (!lox1.begin(0x29) || !lox2.begin(0x30) || !lox3.begin(0x31) || !lox4.begin(0x32)) {
    Serial.println(F("Failed to boot VL53L0X"));
    while (1);
  }

  Serial.println(F("VL53L0X API Simple Ranging example\n\n"));
}

void loop() {
  // Read distances and speeds from all four sensors
  distance1 = distanceDetection(lox1);
  speed1 = speedDetection(lox1);

  distance2 = distanceDetection(lox2);
  speed2 = speedDetection(lox2);

  distance3 = distanceDetection(lox3);
  speed3 = speedDetection(lox3);

  distance4 = distanceDetection(lox4);
  speed4 = speedDetection(lox4);

  // Display distances and speeds on the serial monitor
  Serial.println("Sensor 1:");
  //Serial.print("Distance: ");
  //Serial.println(distance1);
  Serial.print("Speed: ");
  Serial.println(speed1);
  Serial.println();

  Serial.println("Sensor 2:");
 // Serial.print("Distance: ");
 //Serial.println(distance2);
  Serial.print("Speed: ");
  Serial.println(speed2);
  Serial.println();

  Serial.println("Sensor 3:");
 //Serial.print("Distance: ");
 //Serial.println(distance3);
  Serial.print("Speed: ");
  Serial.println(speed3);
  Serial.println();

  Serial.println("Sensor 4:");
  //Serial.print("Distance: ");
  //Serial.println(distance4);
  Serial.print("Speed: ");
  Serial.println(speed4);
  Serial.println();

  // Check for violations
  /*
  checkViolation(speed1, light1);
  checkViolation(speed2, light2);
  checkViolation(speed3, light3);
  checkViolation(speed4, light4);
  */

  delay(1000); // Adjust delay as needed
}

int distanceDetection(Adafruit_VL53L0X lox) {
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);
  if (measure.RangeMilliMeter != 4) {
    return measure.RangeMilliMeter;
  }
  return -1; // Return -1 if measurement is invalid
}

double speedDetection(Adafruit_VL53L0X lox) {
  VL53L0X_RangingMeasurementData_t measure;

  lox.rangingTest(&measure, false);
  int distanceA = measure.RangeMilliMeter;
  unsigned long timeA = millis();
  delay(100); // Adjust delay if needed
  lox.rangingTest(&measure, false);
  int distanceB = measure.RangeMilliMeter;
  unsigned long timeB = millis();

  double distanceChange = distanceA - distanceB;
  double timeChange = (timeB - timeA) / 1000.0; // Convert milliseconds to seconds
  double speed = distanceChange / timeChange; // Speed in mm/s

  return speed;
}

/*
void checkViolation(double speed, TrafficLightColor light) {
  // Check if speed violation occurred
  if (speed > 3000) {
    Serial.print("Sensor ");
    Serial.print(sensorNumber);
    Serial.println(" speed violation detected!");
    speedViolation = true;
  }

  // Check if light violation occurred
  if (light == RED && speed != 0) {
    Serial.print("Sensor ");
    Serial.print(sensorNumber);
    Serial.println(" light violation detected!");
    lightViolation = true;
  }
}
*/