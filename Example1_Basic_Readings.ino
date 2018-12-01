#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "I2Cdev.h"
#include "MPU6050.h"
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MAX30105 particleSensor;

const byte RATE_SIZE = 10; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred


MPU6050 accelgyro;
int16_t ax, ay, az;
int16_t gx, gy, gz;
float beatsPerMinute;
int beatAvg;
#define OUTPUT_READABLE_ACCELGYRO
#define LED_PIN 13
bool blinkState = false;
#define debug Serial //Uncomment this line if you're using an Uno or ESP
//#define debug SerialUSB //Uncomment this line if you're using a SAMD21
#define BAUD_RATE 9600
boolean newData = false;
const byte numChars = 32;
//byte receivedChars[numChars];
//byte tempChars[numChars]; 
//byte messageFromPC[numChars] = {0};
char startMarker = '<';
char endMarker = '>';

void setup()
{ 
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
      Wire.begin();
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
      Fastwire::setup(400, true);
  #endif
  Serial.begin(BAUD_RATE);
  Serial3.begin(BAUD_RATE);
  Serial3.println("ready!");
  Serial.println("MAX30105 Basic Readings Example");
  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

  //Initialize sensor
  if (particleSensor.begin() == false)
  {
    debug.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }

  particleSensor.setup(); //Configure sensor. Use 6.4mA for LED drive
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
  pinMode(LED_PIN, OUTPUT);
}

void loop()
{ 
   accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // these methods (and a few others) are also available
    accelgyro.getAcceleration(&ax, &ay, &az);
    //accelgyro.getRotation(&gx, &gy, &gz);
    //Serial3.print("we are sending data. \n");
    #ifdef OUTPUT_READABLE_ACCELGYRO
        // display tab-separated accel/gyro x/y/z values
        Serial3.print("<");
        Serial3.print("a");
        Serial3.print(",");
        Serial3.print(ax); 
        Serial3.print(",");
        Serial3.print(ay); 
        Serial3.print(",");
        Serial3.print(az); 
//        Serial3.print(gx); Serial3.print(" gy:");
//        Serial3.print(gy); Serial3.print(" gz:");
//        Serial3.println(gz);
        Serial3.print(">");
        Serial3.print("\n");
    #endif

    // blink LED to indicate activity
    blinkState = !blinkState;
    digitalWrite(LED_PIN, blinkState);
    char recvChar;
    //int red = particleSensor.getRed();
    int irValue = particleSensor.getIR();
    //int green = particleSensor.getGreen();
    Serial3.print(startMarker);
    Serial3.print("s");
    Serial3.print(",");
    Serial3.print(irValue);
    Serial3.print(",");
    if (checkForBeat(irValue) == true)
    {
      //We sensed a beat!
      long delta = millis() - lastBeat;
      lastBeat = millis();
  
      beatsPerMinute = 60 / (delta / 1000.0);
  
      if (beatsPerMinute < 255 && beatsPerMinute > 20)
      {
        rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
        rateSpot %= RATE_SIZE; //Wrap variable
  
        //Take average of readings
        beatAvg = 0;
        for (byte x = 0 ; x < RATE_SIZE ; x++)
          beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }
    Serial3.print(beatsPerMinute);
    Serial3.print(",");
    Serial3.print(beatAvg);
    Serial3.print(endMarker);
    Serial3.print("\n");

   if (irValue < 50000){
      Serial3.print(-1);
      Serial3.print(",");
      Serial3.print(-1);
      Serial3.print(endMarker);
      Serial3.print("\n");
  } 
    if(Serial.available()){//check if there's any data sent from the local serial terminal, you can add the other applications here
        //Serial3.println("we are connected to bluetooth");
        recvChar = Serial.read();
        Serial.print("This is the data from comp:");
        Serial.println(recvChar);  
    }
    if (Serial3.available()) {
          Serial.write(Serial3.read());
    }
}
