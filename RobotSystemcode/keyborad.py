import serial
import time
import sys

# Windows 환경에서 키 입력을 실시간으로 받기 위한 msvcrt 라이브러리 사용
import msvcrt

def getch():
    """키보드 입력을 대기하지 않고 즉시 한 글자 읽어오는 함수"""
    return msvcrt.getch().decode('utf-8').lower()

# 시리얼 포트 설정 (사용자 환경에 맞게 포트 번호 확인 필요, 예: 'COM3' 등)
# 젯슨이나 리눅스 환경인 경우 기존 '/dev/ttyACM0' 사용
try:
    ser = serial.Serial('COM3', 115200, timeout=1) 
except:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

print("조종 시작: W(전진강화), S(후진확실), A/D(조향), Space(정지), Q(종료)")

# 초기 상태 값
throttle = 90
steer = 90

# 속도 제어 및 데이터 폭주 방지를 위한 변수 선언
last_send_time = 0
SEND_INTERVAL = 0.05  # 0.05초(20Hz) 간격으로만 데이터를 전송하여 데이터 과부하 방지

try:
    while True:
        # 키보드 입력이 있을 때만 제어값 업데이트
        if msvcrt.kbhit():
            key = getch()
            
            if key == 'w':
                throttle = 115  # 전진 출력 강화 (속도 변환)
                steer = 90
            elif key == 's':
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
                print("\n조종을 종료합니다.")
                break

        # 현재 시간 확인
        current_time = time.time()
        
        # 주기적 전송(SEND_INTERVAL)을 통한 모터 반응 속도 최적화 및 시리얼 데이터 버퍼 오버플로우 방지
        if current_time - last_send_time >= SEND_INTERVAL:
            msg = f"{steer},{throttle}\n"
            ser.write(msg.encode())
            print(f"\r[속도 변환 제어 중] 조향: {steer}, 스로틀: {throttle} ", end="")
            last_send_time = current_time

except KeyboardInterrupt:
    pass
finally:
    # 종료 시 반드시 정지 신호 인가 및 포트 닫기
    ser.write(b"90,90\n")
    ser.close()