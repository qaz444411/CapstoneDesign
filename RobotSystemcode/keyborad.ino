#include <Servo.h>

Servo Steering_servo;
Servo Driving_servo;

void setup() {
  Serial.begin(115200);
  
  Steering_servo.attach(54); 
  Driving_servo.attach(55);
  
  // ESC 초기화 (중립 신호 전달)
  Steering_servo.write(90);
  Driving_servo.write(90);
  delay(2000); // ESC가 중립을 인식할 시간
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int commaIndex = data.indexOf(',');

    if (commaIndex != -1) {
      int steer = data.substring(0, commaIndex).toInt();
      int throttle = data.substring(commaIndex + 1).toInt();

      // [출력 강화] 배터리 무게를 고려해 범위를 45~135 정도로 확장 (기존 90 기준)
      // 90(정지), 110 이상(전진), 70 이하(후진)
      steer = constraint(steer, 45, 135);
      throttle = constraint(throttle, 45, 135); 

      Steering_servo.write(steer);
      Driving_servo.write(throttle);
    }
  }
}