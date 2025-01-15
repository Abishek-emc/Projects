#include <AFMotor.h>
#include<LiquidCrystal_I2C.h>
#include<Servo.h>
Servo ver;
Servo hor;
int a;
char status;
#define servo1 10
#define servo2 9
int ver_position = 90;
int hor_position = 90;
int ftrigpin = A1;
int fechopin = A0;
int btrigpin = A2;
int bechopin = A3;
LiquidCrystal_I2C lcd(0x27,16,2);

int fvalue,bvalue;
char command;

AF_DCMotor left1(1,MOTOR12_1KHZ);
AF_DCMotor left2(2,MOTOR12_1KHZ);
AF_DCMotor right2(3,MOTOR12_1KHZ);
AF_DCMotor right1(4,MOTOR12_1KHZ);

void stop(){
  left1.setSpeed(0);
  left1.run(RELEASE);
  left2.setSpeed(0);
  left2.run(RELEASE);
  right1.setSpeed(0);
  right1.run(RELEASE);
  right2.setSpeed(0);
  right2.run(RELEASE);
}

void brake(char k){
  if (k == 'F'){
      left1.setSpeed(255); 
      left1.run(BACKWARD);
      left2.setSpeed(255); 
      left2.run(BACKWARD);
      right1.setSpeed(255); 
      right1.run(BACKWARD);
      right2.setSpeed(255); 
      right2.run(BACKWARD);
      delay(100);
      stop();
  }
  else if (k == 'B'){
    left1.setSpeed(255); 
    left1.run(FORWARD);  
    left2.setSpeed(255); 
    left2.run(FORWARD); 
    right1.setSpeed(255); 
    right1.run(FORWARD);  
    right2.setSpeed(255); 
    right2.run(FORWARD);
    delay(100);
    stop();
  }
}

int frontread(){
  digitalWrite(ftrigpin,0);
  delayMicroseconds(10);
  digitalWrite(ftrigpin,1);
  delayMicroseconds(10);
  digitalWrite(ftrigpin,0);
  int ping = pulseIn(fechopin,1);
  int value = ping *(0.034/2);
  int mvalue = map(value,30,50,0,150);
  mvalue = constrain(mvalue,0,150);
  return mvalue;
}

int backread(){
  digitalWrite(btrigpin,0);
  delayMicroseconds(10);
  digitalWrite(btrigpin,1);
  delayMicroseconds(10);
  digitalWrite(btrigpin,0);
  int ping = pulseIn(bechopin,1);
  int value = ping *(0.034/2);
  int mvalue = map(value,30,50,0,150);
  mvalue = constrain(mvalue,0,150);
  return mvalue;
}

void forward_run() {
  while (true) {
    int mspeed = frontread();

    left1.setSpeed(mspeed);
    left1.run(FORWARD);
    left2.setSpeed(mspeed);
    left2.run(FORWARD);
    right1.setSpeed(mspeed);
    right1.run(FORWARD);
    right2.setSpeed(mspeed);
    right2.run(FORWARD);


    if (Serial.available() > 0) {
      char command = Serial.read();
      if (command == 'S') {
        stop();  // Implement your stop function here
        break;        // Exit the loop
      }
    }

    // Add a delay to control the loop execution frequency
    delay(100); // Adjust as needed
  }
}

void backward_run(){
  while (true) {
    int mspeed = backread();

    left1.setSpeed(mspeed);
    left1.run(BACKWARD);
    left2.setSpeed(mspeed);
    left2.run(BACKWARD);
    right1.setSpeed(mspeed);
    right1.run(BACKWARD);
    right2.setSpeed(mspeed);
    right2.run(BACKWARD);

    // Check for Bluetooth command to stop or other stop conditions
    if (Serial.available() > 0) {
      char command = Serial.read();
      if (command == 'S') {
        stop();  // Implement your stop function here
        break;        // Exit the loop
      }
    }

    // Add a delay to control the loop execution frequency
    delay(100); // Adjust as needed
  }
}
 

void left(){
  left1.setSpeed(255);
  left1.run(BACKWARD);
  left2.setSpeed(255);
  left2.run(BACKWARD);
  right1.setSpeed(255);
  right1.run(FORWARD);
  right2.setSpeed(255);
  right2.run(FORWARD);
} 

void right(){
  left1.setSpeed(255);
  left1.run(FORWARD);
  left2.setSpeed(255);
  left2.run(FORWARD);
  right1.setSpeed(255);
  right1.run(BACKWARD);
  right2.setSpeed(255);
  right2.run(BACKWARD);
} 


void setup() {
  Serial.begin(9600);
  ver.attach(servo1);
  hor.attach(servo2);
  lcd.init();
  lcd.backlight();
  pinMode(ftrigpin,OUTPUT);
  pinMode(fechopin,INPUT);
  pinMode(btrigpin,OUTPUT);
  pinMode(bechopin,INPUT);

}

void loop() {

  fvalue = frontread();
  bvalue = backread();
  if(fvalue <= 5 || bvalue<=5){
     lcd.clear();
     lcd.setCursor(0,0);
     lcd.print("WARNING!!");
  }

  else{
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("GO-AHEAD!!");
  }
 

  if(Serial.available()>0){
  command = Serial.read();
  switch(command){
    case 'F':
      forward_run();
      break;
    case 'B':
      backward_run();
      break;
    case 'L':
      left();
      break;
    case 'R':
      right();
      break;
    case 'S':
      stop();
      break;  

  }
  if (command == 'N' && ver_position <= 175){
    ver_position +=5;
  }
  if (command == 'S' && ver_position >=5){
    ver_position -=5;
  }
  if (command == 'E' && hor_position >= 5){
    hor_position -=5;
  }
  if (command == 'W' && hor_position <= 175){
    hor_position +=5;
  }
  }
  hor.write(hor_position);
  ver.write(ver_position);
}

