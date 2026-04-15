


#define On 0x0F
#define Off 0x00
#define steering 90
char temp;

typedef struct
{
  byte complete;
  byte cmd;
  byte length;
  byte data;
  byte Start_Stop;
  byte Error;
  byte cs;
  byte steering_value;
  byte speed_value;
}Rx_Frame_Type;
Rx_Frame_Type  Rx_Frame;

volatile boolean state = true;

void GPIO_init()
{
   DDRK= _BV(PORTK7) | _BV(PORTK6) |_BV(PORTK5) |_BV(PORTK4) |_BV(PORTK3) |_BV(PORTK2) |_BV(PORTK1) |_BV(PORTK0);  
   PORTK= 0x00;
   
   pinMode(LED_Pin, OUTPUT);
   pinMode(Buzzer_Pin, OUTPUT);
}

void Timer_init()
{                   
  Timer1.initialize(1000000); //1000000us = 1s  //1초마다 타이머 동작
  Timer1.attachInterrupt(Driver_Oder);  //Driver_Oder 함수를 붙임
}

void LED_ON_Blink()
{
  digitalWrite(LED_BUILTIN, state);    // turn the LED off by making the voltage LOW
  state = !state;
}


/////////////////////////////// LED ////////////////////////////////////////////////
void LED_ON_OFF()
{
  LED_ON();
  delay(500);                       // wait for a second
  LED_OFF();
  delay(500);                       // wait for a second
}
void LED_ON()
{
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
}
void LED_OFF()
{
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
}
/////////////////////////////// Buzzer ////////////////////////////////////////////////

void Buzzer_ON()
{
  //digitalWrite(Buzzer_Pin, LOW);    // turn the LED off by making the voltage LOW
  digitalWrite(Buzzer_Pin, HIGH);   // turn the LED on (HIGH is the voltage level)  
}
void Buzzer_OFF()
{
  //digitalWrite(Buzzer_Pin, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(Buzzer_Pin, LOW);    // turn the LED off by making the voltage LOW
}
void Buzzer_ON_OFF()
{
  Buzzer_ON();
  delay(5);                       // wait for a second
  Buzzer_OFF();
  delay(5);                       // wait for a second
}



void Driver_Oder()
{
//  printf0("\r\nDriver_Oder OK ");                                          
    newAngle = Rx_Frame.steering_value;
    if(newAngle > 44 && newAngle < 180)
    {
      if (newAngle < angle)
      {
        Steering_servo.write(newAngle);
        Driving_servo.write(Rx_Frame.speed_value);
        //printf0("\r\n speed:%d ,steering:%d",Rx_Frame.speed_value,Rx_Frame.steering_value);               
      }
      else if(newAngle > angle)
      {
        Steering_servo.write(newAngle);
        Driving_servo.write(Rx_Frame.speed_value);          
        //printf0("\r\n speed:%d ,steering:%d",Rx_Frame.speed_value,Rx_Frame.steering_value);
      }
      else if(angle == angle)
      {
        Steering_servo.write(angle);
        Driving_servo.write(Rx_Frame.speed_value);          
        //printf0("\r\n speed:%d ,steering:%d",Rx_Frame.speed_value,Rx_Frame.steering_value);
      }
    }  
    else if(newAngle == 0)
    {
      Steering_servo.write(90);
      Driving_servo.write(90);        
      //printf0("\r\n speed:%d ,steering:%d",90,90);
    }   
    else;
    idx = 0;
    angle = newAngle;

    //Ack_Response(Rx_Frame.steering_value,Rx_Frame.speed_value,0,0);
}
