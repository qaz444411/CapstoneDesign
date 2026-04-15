#include <Servo.h>

Servo Steering_servo;
Servo Driving_servo;

void setup() {
  Serial.begin(115200); // NX 보드와 통신 속도 통일
  
  Steering_servo.attach(54); // 기존 핀 번호 유지
  Driving_servo.attach(55);
  
  // 초기화 (정지 및 직진)
  Steering_servo.write(90);
  Driving_servo.write(90);
  
  Serial.println("Keyboard Control Mode Ready");
}

void loop() {
  if (Serial.available() > 0) {
    // NX보드에서 "90,100\n" 형식으로 데이터를 보낸다고 가정
    String data = Serial.readStringUntil('\n');
    int commaIndex = data.indexOf(',');

    if (commaIndex != -1) {
      int steer = data.substring(0, commaIndex).toInt();
      int throttle = data.substring(commaIndex + 1).toInt();

      // 서보 범위 제한 (안전장치)
      steer = constraint(steer, 45, 140);
      throttle = constraint(throttle, 60, 120);

      Steering_servo.write(steer);
      Driving_servo.write(throttle);
      
      // 피드백 (NX 터미널에서 확인용)
      Serial.print("ACK -> S:"); Serial.print(steer);
      Serial.print(" D:"); Serial.println(throttle);
    }
  }
}

// 범위 제한 함수
int constraint(int val, int minV, int maxV) {
  if (val < minV) return minV;
  if (val > maxV) return maxV;
  return val;
}
