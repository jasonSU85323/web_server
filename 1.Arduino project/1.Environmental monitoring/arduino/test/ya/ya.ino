#include <LiquidCrystal_I2C.h>
#include <Bridge.h>


LiquidCrystal_I2C lcd(0x3F, 2, 1 ,0 , 4, 5, 6 ,7 ,3, POSITIVE);
byte dat[5];

void setup() {
Bridge.begin(); // 啟動Bridge
  Serial.begin(9600);

  Bridge.put("one", "1");
  lcd.begin(20, 4);

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
  
  Bridge.put("one", "2");
}

void loop() {
  Bridge.put("one", "3");
  delay(1000);
  
}
