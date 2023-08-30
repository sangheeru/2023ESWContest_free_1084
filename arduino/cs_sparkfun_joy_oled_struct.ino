/* Wireless Joystick Tank Steering Robot Example
 * by: Alex Wende
 * SparkFun Electronics
 * date: 9/28/16
 * 
 * license: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)
 * Do whatever you'd like with this code, use it for any purpose.
 * Please attribute and keep this license.
 * 
 * This is example code for the Wireless Joystick to control a robot
 * using XBee. Plug the first Xbee into the Wireless Joystick board,
 * and connect the second to the SparkFun Serial Motor Driver.
 * 
 * Moving the left and right joystick up and down will change the
 * speed and direction of motor 0 and motor 1. The left trigger will
 * reduce the maximum speed by 5%, while the right trigger button
 * will increase the maximum speed by 5%.
 * 
 * Connections to the motor driver is as follows:
 * XBee - Motor Driver
 *   5V - VCC
 *  GND - GND
 * DOUT - RX
 * 
 * Power the motor driver with no higher than 11V!
 */

#include <SPI.h>
#include <Wire.h>
#include <SFE_MicroOLED.h>

#define PIN_RESET 11  // Connect RST to pin 9 (req. for SPI and I2C)
#define PIN_DC    12  // Connect DC to pin 8 (required for SPI)
#define PIN_CS    10 // Connect CS to pin 10 (required for SPI)
#define DC_JUMPER 0

#define MAX17043_ADDRESS 0x36

// Pin definitions
int alertPin = 7;  // This is the alert interrupt pin, connected to pin 7 on the Wireless Joystick
int ledPin = 13;   // This is the pin the led is connected to

// Global Variables
// float batVoltage;
// float batPercentage;
int batPercentage;
int alertStatus;

MicroOLED oled(PIN_RESET, PIN_DC, PIN_CS);

#define UD_JOY A2  //A3였는데 y축을 세로로 바꾸려고 A2로 바꿈
#define LR_JOY A3  //A2였는데 x축을 가로로 바꾸려고 A3로 바꿈
#define MODE_BTN 6
#define UP_BTN  8
#define DN_BTN  2
#define LT_BTN  4
#define RT_BTN  9

const long baud = 57600;
unsigned long start_time = 0;
unsigned long tmp_time = 0;

int Tms = 20;  // 10ms period
int tot_btn = 0;
int num_connect_cnt = 0;
bool connect_ship = false;
bool logging = false;
int num_connect_timeout = 3;   // sec
int num_connect_timeout_cnt = (int)(1000.0 * num_connect_timeout / Tms); 
bool gnss_err = false;
bool imu_err = false;
bool rudder_err = false;
bool prop_err = false;


int err_code = 0; // 0~7
/* Motor | Rudder | Imu
0  0       0        0    => Connected
1  0       0        1    => Imu(X)
2  0       1        0    => Rudder(X)
3  0       1        1    => Rudder(X), Imu(X)
4  1       0        0    => Motor(X)
5  1       0        1    => Motor(X), Imu(X)         
6  1       1        0    => Motor(X), Rudder(X)
7  1       1        1    => Motor(X), Rudder(X), Imu(X)
*/

struct RcvStruct {
  char header;
  double val[6];
};

unsigned int rcv_struct_size = sizeof(RcvStruct);


struct JoyStruct {
  char header[3];
  int axis[2];
  int btn;
};
JoyStruct joyStruct;
unsigned int snd_struct_size = sizeof(JoyStruct);

void setup() 
{
  oled.begin();  // Start OLED  
  oled.setFontType(0);  // Set the text to small (10 columns, 6 rows worth of characters)
  oled.flipVertical(1);
  oled.flipHorizontal(1);

  Wire.begin();  // Start I2C

  SerialUSB.begin(baud);

  Serial1.begin(baud);
  Serial1.setTimeout(30);

  pinMode(MODE_BTN, INPUT_PULLUP);
  pinMode(UP_BTN, INPUT_PULLUP);
  pinMode(DN_BTN, INPUT_PULLUP);
  pinMode(LT_BTN, INPUT_PULLUP);
  pinMode(RT_BTN, INPUT_PULLUP);

  pinMode(alertPin, INPUT_PULLUP);  // Enable pullup resistor
  configMAX17043(32);  // Configure the MAX17043's alert percentage
  qsMAX17043();  // restart fuel-gauge calculations
  
  joyStruct.header[0] = 'J';
  joyStruct.header[1] = 'O';
  joyStruct.header[2] = 'Y';
  
}


void loop() 
{        
  // checkConnect();  
  if (millis() - start_time > Tms) {
    // oledDisp(); // requires 9ms!
    sendJoy();    
    start_time = millis();
  } 
}


void checkConnect() 
{
  if (Serial1.available() >= rcv_struct_size) {
    RcvStruct rcvStruct;
    Serial1.readBytes((byte*)&rcvStruct, rcv_struct_size);    
    
    // SerialUSB.println(rcv_str);
    if (rcvStruct.header == 'S') {
      num_connect_cnt = 0;
      connect_ship = true;
      logging = true;
      SerialUSB.println((String)"Logging");
    } else if (rcvStruct.header == 'E') {
      num_connect_cnt = 0;
      connect_ship = true;
      logging = false;      
      err_code = int(rcvStruct.val[0]);
      SerialUSB.println((String)"Error code:" + err_code);
    }
  }
}


void sendJoy() 
{  
  joyStruct.axis[0] = analogRead(UD_JOY);
  joyStruct.axis[1] = analogRead(LR_JOY);  
  int mode_btn = digitalRead(MODE_BTN); 
  int up_btn = digitalRead(UP_BTN); 
  int dn_btn = digitalRead(DN_BTN); 
  int lt_btn = digitalRead(LT_BTN); 
  int rt_btn = digitalRead(RT_BTN); 

  // manual mode: 0~5, autopilot mode: 10~15
  int tot_btn = 0;
  if (mode_btn == 0) {
    tot_btn = 10;    
  }
  if (up_btn == 0 ) {
    tot_btn += 1;
  } else if (dn_btn == 0 ) {
    tot_btn += 2;
  } else if (lt_btn == 0 ) {
    tot_btn += 3;
  } else if (rt_btn == 0 ) {
    tot_btn += 4;
  } else {
    tot_btn += 5;
  }
  joyStruct.btn = tot_btn;
  Serial1.write((byte*)&joyStruct, snd_struct_size);
}


void oledDisp()
{
  batPercentage = percentMAX17043();  // Get battery percentage
  // batVoltage = (float) vcellMAX17043() * 1/800;  // vcell reports battery in 1.25mV increments
  alertStatus = digitalRead(alertPin);

  oled.clear(PAGE); // clears the screen
  oled.setCursor(0,0);  // move cursor to top left corner
  if(connect_ship){
    if(logging) {
      oled.print("Log (");        
    } else {
      oled.print("Con ("); 
    }  
  } else{
    oled.print("NC (");
    err_code = 0;
  }

  if(alertStatus == LOW){
    oled.print("Low)\n\n");
  }
  else{
    oled.print(batPercentage);
    oled.print("%)\n\n");
  }  

  if (connect_ship) {
    gnss_err = false;
    imu_err = false;
    rudder_err = false;
    prop_err = false;
    if((err_code >> 0) & 1) {         
      gnss_err = true;
    }
    if((err_code >> 1) & 1) {      
      rudder_err = true;
    }
    if((err_code >> 2) & 1) {      
      prop_err = true;
    }
    if((err_code >> 3) & 1) {   
      imu_err = true;
    }

    if(gnss_err) {         
      oled.print(" GNSS (X)\n");
    } else {
      oled.print(" GNSS (O)\n");
    }
    if(imu_err) {   
      oled.print(" IMU  (X)\n");
    } else {
      oled.print(" IMU  (O)\n");
    }
    if(rudder_err) {      
      oled.print(" Rudd (X)\n");
    } else {
      oled.print(" Rudd (O)\n");
    }
    if(prop_err) {      
      oled.print(" Prop (X)\n");
    } else {
      oled.print(" Prop (O)\n");
    }
  }
    
  oled.display();
  // delay(10);  

}

/*
vcellMAX17043() returns a 12-bit ADC reading of the battery voltage,
as reported by the MAX17043's VCELL register.
This does not return a voltage value. To convert this to a voltage,
multiply by 5 and divide by 4096.
*/
// unsigned int vcellMAX17043()
// {
//   unsigned int vcell;

//   vcell = i2cRead16(0x02);
//   vcell = vcell >> 4;  // last 4 bits of vcell are nothing

//   return vcell;
// }

/*
percentMAX17043() returns a float value of the battery percentage
reported from the SOC register of the MAX17043.
*/

float percentMAX17043()
{
  unsigned int soc;
  float percent;

  soc = i2cRead16(0x04);  // Read SOC register of MAX17043
  percent = (byte) (soc >> 8);  // High byte of SOC is percentage
  percent += ((float)((byte)soc))/256;  // Low byte is 1/256%

  return percent;
}

/* 
configMAX17043(byte percent) configures the config register of
the MAX170143, specifically the alert threshold therein. Pass a 
value between 1 and 32 to set the alert threshold to a value between
1 and 32%. Any other values will set the threshold to 32%.
*/
void configMAX17043(byte percent)
{
  if ((percent >= 32)||(percent == 0))  // Anything 32 or greater will set to 32%
    i2cWrite16(0x9700, 0x0C);
  else
  {
    byte percentBits = 32 - percent;
    i2cWrite16((0x9700 | percentBits), 0x0C);
  }
}

/* 
qsMAX17043() issues a quick-start command to the MAX17043.
A quick start allows the MAX17043 to restart fuel-gauge calculations
in the same manner as initial power-up of the IC. If an application's
power-up sequence is very noisy, such that excess error is introduced
into the IC's first guess of SOC, the Arduino can issue a quick-start
to reduce the error.
*/
void qsMAX17043()
{
  i2cWrite16(0x4000, 0x06);  // Write a 0x4000 to the MODE register
}

/* 
i2cRead16(unsigned char address) reads a 16-bit value beginning
at the 8-bit address, and continuing to the next address. A 16-bit
value is returned.
*/
unsigned int i2cRead16(unsigned char address)
{
  int data = 0;

  Wire.beginTransmission(MAX17043_ADDRESS);
  Wire.write(address);
  Wire.endTransmission();

  Wire.requestFrom(MAX17043_ADDRESS, 2);
  while (Wire.available() < 2)
    ;
  data = ((int) Wire.read()) << 8;
  data |= Wire.read();

  return data;
}

/*
i2cWrite16(unsigned int data, unsigned char address) writes 16 bits
of data beginning at an 8-bit address, and continuing to the next.
*/
void i2cWrite16(unsigned int data, unsigned char address)
{
  Wire.beginTransmission(MAX17043_ADDRESS);
  Wire.write(address);
  Wire.write((byte)((data >> 8) & 0x00FF));
  Wire.write((byte)(data & 0x00FF));
  Wire.endTransmission();
}




















