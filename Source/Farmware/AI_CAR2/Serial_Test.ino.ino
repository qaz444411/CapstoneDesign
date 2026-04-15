

/*====================================================================*/
/*                                                                    */
/*             AI Car Servo Motor Control 20231116                    */
/*             Arduino Mega2560 + R470 Car Body                       */
/*                                                                    */
/*                                                                    */
/*====================================================================*/ 
              
#include <TimerOne.h>  //라이브러리 추가
#include <Servo.h>

#define LED_Pin 13
#define Buzzer_Pin 12
#define NEUTRAL 90
#define REVERSE 206
#define FORWARD 409
const int SteeringPin =  54;
const int ForwordPin =  55;

//Servo servomotor;

Servo Steering_servo;
Servo Driving_servo;
Servo Transmission_servo;

int Steering_value = 90;
int Driving_value = 90; 
int Transmission_value = 135;

int newAngle = 0;
int start = 10;
int speed = 90;
int angle = 0;
const int MaxChars = 4;
char strValue[MaxChars+1];
int idx = 0;
unsigned int SteeringPWM;
unsigned int ForwardPWM;
     

boolean BL = false;  //스위치 false로 초기화


void setup()
{
  // put your setup code here, to run once:
  GPIO_init();
  Buzzer_OFF();
  pinMode(SteeringPin, OUTPUT);
  pinMode(ForwordPin, OUTPUT);
  
  Steering_servo.attach(54);     //servo 서보모터 54번 핀에 연결
  Driving_servo.attach(55);     //servo 서보모터 55번 핀에 연결
  Transmission_servo.attach(56);     //servo 서보모터 56번 핀에 연결

  Steering_servo.write(Steering_value); //value값의 각도로 회전. ex) value가 90이라면 90도 회전
  Driving_servo.write(Driving_value); //value값의 각도로 회전. ex) value가 90이라면 90도 회전
  Transmission_servo.write(Transmission_value); //value값의 각도로 회전. ex) value가 90이라면 90도 회전

  Uart_init();
  Timer_init();

  Buzzer_ON_OFF();
  Buzzer_ON_OFF();

  LED_ON_OFF();
  SteeringPWM = NEUTRAL;
  ForwardPWM = NEUTRAL;
 
  analogWrite(SteeringPin, SteeringPWM);
  analogWrite(ForwordPin, ForwardPWM);
  //delay(1000);
  angle = 90;
}


void blinkLED()
{
  BL = !BL;
  digitalWrite(13, BL);
}

  
void loop()
{
  //printf0("\r\n Hello, AI CAR!!",0);
  //float BAT_Voltage = (analogRead(A5) * 24.00) / 1023;
  //BAT_Sensing();
  //Driver_Oder();
  //delay(1000);
}
