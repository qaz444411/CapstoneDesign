import serial
import time
# (getch 함수 정의 부분은 동일하므로 생략)

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

print("조종 시작: W(전진강화), S(후진확실), A/D(조향), Space(정지)")

try:
    while True:
        key = getch()
        
        if key == 'w':
            # 배터리가 무거우면 96 대신 110~120 정도로 높게 줍니다.
            throttle = 115  # 전진 출력 강화
            steer = 90
        elif key == 's':
            # 후진이 안 될 경우 값을 더 낮게(70 이하) 줘서 ESC에 신호를 줍니다.
            # 어떤 ESC는 90(중립) -> 70(브레이크) -> 90(중립) -> 70(후진) 순서가 필요할 수 있음
            throttle = 65   # 확실한 후진 신호
            steer = 90
        elif key == 'a':
            steer = 130     # 좌회전
        elif key == 'd':
            steer = 50      # 우회전
        elif key == ' ':
            throttle = 90   # 정지
            steer = 90
        elif key == 'q':
            break

        msg = f"{steer},{throttle}\n"
        ser.write(msg.encode())
        print(f"\r현재 상태 -> 조향: {steer}, 스로틀: {throttle} (전송 중...)", end="")

except KeyboardInterrupt:
    pass
finally:
    ser.write(b"90,90\n")
    ser.close()