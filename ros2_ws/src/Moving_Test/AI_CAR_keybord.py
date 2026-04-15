import serial
import sys
import tty
import termios

# 시리얼 설정
ser = serial.Serial('/dev/ttyUSB_DRV0', 115200, timeout=1)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

print("조종 시작: W(전진), S(후진), A(좌), D(우), Space(정지), Q(종료)")

steer = 90
throttle = 90

try:
    while True:
        key = getch()
        
        if key == 'w':
            throttle = 100 # 살짝 전진
        elif key == 's':
            throttle = 80  # 살짝 후진
        elif key == 'a':
            steer = 120    # 왼쪽
        elif key == 'd':
            steer = 60     # 오른쪽
        elif key == ' ':
            steer = 90
            throttle = 90
        elif key == 'q':
            break

        # 아두이노로 전송
        msg = f"{steer},{throttle}\n"
        ser.write(msg.encode())
        print(f"\rSending: {msg.strip()}", end="")

except KeyboardInterrupt:
    pass
finally:
    ser.write(b"90,90\n") # 종료 시 정지
    ser.close()
