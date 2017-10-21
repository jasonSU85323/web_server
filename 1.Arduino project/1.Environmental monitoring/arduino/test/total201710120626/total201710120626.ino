#include "DHT.h"
#define DHTPIN 7     // what digital pin we're connected to
#define DHTTYPE DHT11   // DHT 11
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>
#include <Process.h>

const int sensorIn = A0;
int mVperAmp = 185; // use 100 for 20A Module and 66 for 30A Module

double Voltage = 0;
double VRMS = 0;
double AmpsRMS = 0;

int measurePin = A3; //Connect dust sensor to Arduino A0 pin
int ledPower = 3;   //Connect 3 led driver pins of dust sensor to Arduino D2
int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;
float voMeasured = 0;
float calcVoltage = 0;
float dustDensity = 0;

DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal_I2C lcd(0x3F, 2, 1 ,0 , 4, 5, 6 ,7 ,3, POSITIVE);
byte dat[5];

YunServer server; // 建立YunServer物件
void setup() {
  Bridge.begin(); // 啟動Bridge
  Serial.begin(9600);


  dht.begin();
  pinMode(ledPower,OUTPUT);


  //lcd.begin(20, 4);
 // 閃爍三次
  for(int i = 0; i < 3; i++) {
  lcd.backlight(); // 開啟背光
  delay(1000);
  lcd.noBacklight(); // 關閉背光
  delay(1000);
  }
  lcd.backlight();


  // 輸出初始化文字
  lcd.setCursor(0, 0); // 設定游標位置在第一行行首
  lcd.print("ICshop&MakerPRO");
  
  lcd.setCursor(0, 1); // 設定游標位置在第二行行首
  lcd.print("Hello, Maker!");

  lcd.setCursor(0, 2); // 設定游標位置在第二行行首
  lcd.print("Hello, Maker!");

  lcd.setCursor(0, 3); // 設定游標位置在第二行行首
  lcd.print("Hello, Maker!");
  delay(2000);
  lcd.clear(); //顯示清除
  
}

void loop() {

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);
  
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  
  float hif = dht.computeHeatIndex(f, h);
  float hic = dht.computeHeatIndex(t, h, false);

  
  float sensorVoltage; 
  float sensorValue;
  sensorValue = analogRead(A1);
  sensorVoltage = sensorValue/1024*5.0;

  Voltage = getVPP();
  VRMS = (Voltage/2.0) *0.707; 
  AmpsRMS = (VRMS * 1000)/mVperAmp;

  digitalWrite(ledPower,LOW); // power on the LED
  delayMicroseconds(samplingTime);
  voMeasured = analogRead(measurePin); // read the dust value
  delayMicroseconds(deltaTime);
  digitalWrite(ledPower,HIGH); // turn the LED off
  delayMicroseconds(sleepTime);
  // 0 - 5V mapped to 0 - 1023 integer values
  // recover voltage
  calcVoltage = voMeasured * (5.0 / 1024.0);
  // linear eqaution taken from http://www.howmuchsnow.com/arduino/airquality/
  // Chris Nafis (c) 2012
  dustDensity = 0.17 * calcVoltage - 0.1;



  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.print(" *C ");
  Serial.print(f);
  Serial.print(" *F\t");
  Serial.print("Heat index: ");
  Serial.print(hic);
  Serial.print(" *C ");
  Serial.print(hif);
  Serial.println(" *F");
  
  Serial.print("sensor voltage = ");
  Serial.print(sensorVoltage);
  Serial.println(" V");

  Serial.print(AmpsRMS);
  Serial.println(" Amps RMS");

  Serial.print("Raw Signal Value (0-1023): ");
  Serial.print(voMeasured);
  Serial.print(" - Voltage: ");
  Serial.print(calcVoltage);
  Serial.print(" - Dust Density: ");
  Serial.print(dustDensity * 1000); // 這裡將數值呈現改成較常用的單位( ug/m3 )
  Serial.println(" ug/m3 ");

  lcd.setCursor(0, 0); // 設定游標位置在第一行行首
  lcd.print("Humidity: ");
  lcd.print(h);
  lcd.setCursor(0, 1); // 設定游標位置在第一行行首
  lcd.print("Temperature C:");
  lcd.print(hic);
  lcd.setCursor(0, 2); // 設定游標位置在第一行行首
  lcd.print("Temperature F:");
  lcd.print(hif);
  lcd.setCursor(0, 3); // 設定游標位置在第一行行首
  lcd.print("sensor:");
  lcd.print(sensorVoltage);

  delay(2000);
  lcd.clear(); //顯示清除

  lcd.setCursor(0, 0); // 設定游標位置在第一行行首
  lcd.print("AirQuality:");
  lcd.print(voMeasured);
  lcd.setCursor(0, 1); // 設定游標位置在第一行行首
  lcd.print("DustDensity:");
  lcd.print(dustDensity  * 1000);
  lcd.setCursor(0, 2); // 設定游標位置在第一行行首;lcd.setCursor(0, 2); // 設定游標位置在第一行行首
  lcd.print("ampere:");
  lcd.print(AmpsRMS);
  
  Bridge.put("Humidity", String(h));
  Bridge.put("TemperC", String(hic));
  Bridge.put("TemperF", String(hif));
  Bridge.put("sensor", String(sensorVoltage));
  Bridge.put("Air", String(voMeasured));
  Bridge.put("Dust", String(dustDensity*1000));
  Bridge.put("ampere", String(AmpsRMS));
  Bridge.put("one", String(h));
  
  delay(1000);
}

float getVPP()
{
  float result;
  int readValue;             //value read from the sensor
  int maxValue = 0;          // store max value here+*
  int minValue = 1024;          // store min value here 
   uint32_t start_time = millis();
   while((millis()-start_time) < 1000) //sample for 1 Sec
   {
       readValue = analogRead(sensorIn);
       // see if you have a new maxValue
       if (readValue > maxValue) 
       {
           /*record the maximum sensor value*/
           maxValue = readValue;
       }
       if (readValue < minValue) 
       {
           /*record the maximum sensor value*/
           minValue = readValue;
       }
   }
   // Subtract min from max
   result = ((maxValue - minValue) * 5.0)/1024.0;    
   return result;
 }
