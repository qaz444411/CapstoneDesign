#include <Servo.h>

void setup() {
  Serial.begin(115200);
  pinMode(A0, INPUT); // 배터리 전압 측정 핀
}

void loop() {
  int v0 = analogRead(A0);
  int v1 = analogRead(A1);
  int v2 = analogRead(A2);

  // 일단 A0, A1, A2 중 가장 높은 값을 배터리 값으로 가정해봅니다.
  int maxRaw = max(v0, max(v1, v2));
  byte v_data = map(maxRaw, 0, 1023, 0, 255);

  byte packet[8] = {0xEA, 0x03, 0x00, 0x00, 0x00, v_data, 0x00, 0x03};
  
  // 체크섬 계산
  byte checksum = ~(packet[1] + packet[2] + packet[3] + packet[4] + packet[5]) + 1;
  packet[6] = checksum;

  Serial.write(packet, 8);
  
  // 시리얼 모니터 확인용 (NX에서 확인할 땐 주석 처리해도 됨)
  // Serial.print("A0:"); Serial.print(v0); Serial.print(" A1:"); Serial.println(v1);
  
  delay(500);
}
