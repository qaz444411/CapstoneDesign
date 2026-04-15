#필요한 패키지.모듈.함수 불러오기. 
#파이썬 코드는 임포팅 이라는 프로세스를 통해 다른 패키지나 모듈 혹은 (내장.외장)함수에 있는 코드들에 대한 접근권을 얻습니다.
from rplidar import RPLidar
import time
from serial import Serial

#터미널 창에서 'ls /dev/tty*'로 아두이노 보드와 연결된 USB가 몇번으로 잡혀있는지 확인해주어야 한다.
ser = Serial('/dev/arduino',115200,timeout=1)
lidar = RPLidar('/dev/lidar',115200)
#(예)아두이노쪽 연결 USB선을 뺀 후에 ‘ls /dev/tty*’로 확인한다.

#RPLidar의 상태 확인
info = lidar.get_info()
print(info)
health = lidar.get_health()
print(health)

print ("starting spinning .......\n")
time.sleep(5)
print ("scanning started")

def create_command(steering, speed):
    STX = 0xEA
    ETX = 0x03

    # Calculate Length
    Length = 0x03

    # Set dummy values
    dummy1 = 0x00
    dummy2 = 0x00

    # Calculate Checksum
    Checksum = ((~(Length + steering + speed + dummy1 + dummy2)) & 0xFF) + 1

    # Create the command bytearray
    command = bytearray([STX, Length, steering, speed, dummy1, dummy2, Checksum, ETX])

    return command

ser = Serial('/dev/arduino', 115200, timeout=0.5)
strval, spdval = 0x5A, 0x30

a = float(input("enter a:"))
b = float(input("enter b:"))

#lidar.iter_scans()로 올라오는 정보를 받아서 설정한 각도와 거리에 있는 장애물을 탐지하고 모터를 제어하는 동작을 수행한다.
try:
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            
            if (a < angle < b):

                print(angle,"\n")
                print(distance,"\n")


except KeyboardInterrupt: #예외처리: KeyboardInterrupt를 설정해두었다.
    print('Stoping.')
    lidar.stop()          
    lidar.stop_motor()     
    lidar.disconnect()

