#include "Adafruit_VL53L0X.h"

#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31
#define LOX3_ADDRESS 0x32
#define LOX4_ADDRESS 0x33

#define SHT_LOX1 19 //White
#define SHT_LOX2 18 //Blue
#define SHT_LOX3 5 //Black
#define SHT_LOX4 4 //Brown
//SDA (GREEN) PIN 21
//SCL (YELLOW) PIN 22

#define hallSensorE 14 //Grey
#define hallSensorS 27 //blue
#define hallSensorN 26 //Brown

#define toCamera 13

Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox3 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox4 = Adafruit_VL53L0X();

int distance1;
int distance2;
int distance3;
int distance4;
double speed1;
double speed2;
double speed3;
double speed4;

int speedLimit;

bool isNorth_South = true;
bool speedViolation = false;
bool lightViolation = false;

bool carPresenceE = false;
bool carPresenceN = false;
bool carPresenceS = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  speedLimit = 30;

  pinMode(hallSensorN, INPUT);
  pinMode(hallSensorS, INPUT);
  pinMode(hallSensorE, INPUT);
  pinMode(toCamera, OUTPUT);

  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);
  pinMode(SHT_LOX3, OUTPUT);
  pinMode(SHT_LOX4, OUTPUT);

  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  
  delay(10);

  setID();
}

void loop() {
  // Read distances and speeds from only active ways
  if(isNorth_South){
    distance1 = distanceDetection(lox1)/10;
    speed1 = speedDetection(lox1);

    distance2 = distanceDetection(lox2)/10;
    speed2 = speedDetection(lox2);
    Serial.println("Sensor 1:");
    Serial.print("Distance: ");
    Serial.println(distance1);
    Serial.print("Speed: ");
    Serial.println(speed1);
    Serial.println();

    Serial.println("Sensor 2:");
    Serial.print("Distance: ");
    Serial.println(distance2);
    Serial.print("Speed: ");
    Serial.println(speed2);
    Serial.println();

    checkViolation(speed1, 1);
    checkViolation(speed2, 2);
    if (digitalRead(hallSensorE) == LOW){
      Serial.println("Car presence detected on east side!");
      carPresenceE = true;
    }else{
      carPresenceE = false;
    }

  }else{
    distance3 = distanceDetection(lox3)/10;
    speed3 = speedDetection(lox3);

    distance4 = distanceDetection(lox4)/10;
    speed4 = speedDetection(lox4);

    Serial.println("Sensor 3:");
    Serial.print("Distance: ");
    Serial.println(distance3);
    Serial.print("Speed: ");
    Serial.println(speed3);
    Serial.println();

    Serial.println("Sensor 4:");
    Serial.print("Distance: ");
    Serial.println(distance4);
    Serial.print("Speed: ");
    Serial.println(speed4);
    Serial.println();

    checkViolation(speed3, 3);
    checkViolation(speed4, 4);
    if (digitalRead(hallSensorN) == LOW){
      carPresenceN = true;
    }else{
      carPresenceN = false;
    }
    if (digitalRead(hallSensorE) == LOW){
      carPresenceS = true;
    }else{
        carPresenceS = false;
    }
  }    
  // Check for violations


  if(speedViolation || lightViolation){
    digitalWrite(toCamera, HIGH);
    delay(100);  
    speedViolation = false;
    lightViolation = false;
    digitalWrite(toCamera, LOW);
  } 

  delay(200); // Adjust delay as needed
}

void setID() {
  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  digitalWrite(SHT_LOX3, HIGH);
  digitalWrite(SHT_LOX4, HIGH);
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  delay(10);

  pinMode(SHT_LOX1, INPUT);
  while (!lox1.begin(LOX1_ADDRESS, true)) {
    Serial.println(F("Failed to boot first VL53L0X"));
    delay (1000);
  }
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);

  if (!lox2.begin(LOX2_ADDRESS)) {
    Serial.println(F("Failed to boot second VL53L0X"));
    while (1);
  }
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  digitalWrite(SHT_LOX3, HIGH);
  digitalWrite(SHT_LOX4, LOW);

  if (!lox3.begin(LOX3_ADDRESS)) {
    Serial.println(F("Failed to boot third VL53L0X"));
    while (1);
  }
  delay(10);

  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  digitalWrite(SHT_LOX3, HIGH);
  digitalWrite(SHT_LOX4, HIGH);

  if (!lox4.begin(LOX4_ADDRESS)) {
    Serial.println(F("Failed to boot fourth VL53L0X"));
    while (1);
  }
  delay(10);
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
  int distanceA = measure.RangeMilliMeter/10;
  double speed = 0;
  if(distanceA < 35){
    unsigned long timeA = millis();
    delay(100); // Adjust delay if needed
    lox.rangingTest(&measure, false);
    int distanceB = measure.RangeMilliMeter/10;
    if(distanceB > 35)
      distanceB = 35;
    unsigned long timeB = millis();
    double distanceChange = distanceA - distanceB;
    double timeChange = (timeB - timeA) / 1000.0; // Convert milliseconds to seconds
    speed = (distanceChange) / timeChange; // Speed in cm/s
    return speed;
  }
  return speed;
}


void checkViolation(double speed, int sensorNumber) {
  // Check if speed violation occurred
  if (speed > speedLimit) {
    Serial.print("Sensor ");
    Serial.print(sensorNumber);
    Serial.println(" speed violation detected!");
    speedViolation = true;
  }


  if(isNorth_South){
    if (carPresenceE == true && digitalRead(hallSensorE) == HIGH){
      lightViolation = true;
      Serial.println("light violation detected in the east side!");
    }
  }
  else{
    if (carPresenceN == true && digitalRead(hallSensorN) == HIGH){
      lightViolation = true;
    }
    if (carPresenceS == true && digitalRead(hallSensorS) == HIGH){
      lightViolation = true;
    }

  }
}
