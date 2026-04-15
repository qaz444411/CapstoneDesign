import os
import sys
import time
import numpy as np

from pathlib import Path
from rplidar import RPLidar
from serial import Serial

#sys.stdout = open('stdout.txt', 'w')
#logFile = open('log.txt', 'w')

ttyARDUINO = Path('/dev/ttyARDUINO')
if (ttyARDUINO.exists()) :
    arduino = Serial('/dev/ttyARDUINO', 115200, timeout=1)
    time.sleep(2)
else:
    quit()

## RpLiDAR
ttyLiDAR = Path('/dev/ttyLiDAR')
if (ttyLiDAR.exists()) :
    lidar = RPLidar('/dev/ttyLiDAR', 115200)
    info = lidar.get_info()
    print('RpLidar :', info)

    health = lidar.get_health()
    print('RpLidar :', health)
else :
    quit()

LiDAR = [0]*180
sDegree, sDistance = 0, 0

steering = str('0')
prevSteering = str('0')

def GetAverage(array) :
    total, cnt, result = 0, 0, 0
    for i in array :
        if (i>0) :
            total += i
            cnt += 1

    if (total > 0) and (cnt > 0) :
        result = total / cnt

    return int(result)

try:
    for scan in lidar.iter_scans() :
        #print('->', len(scan), scan)
        #np.savetxt('logFile.txt', np.array(LiDAR).reshape(18,10))
        LiDAR = [0]*180

        #arduino.write(steering.encode())

        if (steering != prevSteering) :
            prevSteering = steering
            arduino.write(steering.encode())
            if steering == '0' :
                print('[AI Car Stop]')
            else :
                print('[AI Car Go  ]:%3s[%.2f]' %(steering, sDistance))
                                
        for (_, angle, distance) in scan :
            if (angle >= 0.0) and (angle < 90.0) :
                index = int(angle)+90
                LiDAR[index] = int(distance)
                

            elif (angle >= 270.0) and (angle < 360.0) :
                index = int(angle)-270
                LiDAR[index] = int(distance)
                
        ## For RpLiDAR Scanning Value Monitering 
        #print(np.array(LiDAR).reshape(18,10), end='\n')

        ## Steering Control
        if True :
            sDistance = GetAverage(LiDAR[70:110])

            if (sDistance < 400) and (sDistance > 100) :
                steering = str(0)
                
            else :
                if GetAverage(LiDAR[0:45]) < 300 :
                    #print('Steering Right Max')
                    steering = str(135)
                    
                elif GetAverage(LiDAR[135:180]) < 300 :
                    #print('Steering Left Max')
                    steering = str(45)
                    
                else :
                    if GetAverage(LiDAR[50:130]) > 1500 :
                        steering = str(90)
                    else :
                        sDegree = LiDAR.index(max(LiDAR[50:130]))
                        sDistance = LiDAR[sDegree]
                        steering = str(sDegree)
                        
except KeyboardInterrupt:
    print('''\nKeyboardInterrupt''')

if (ttyLiDAR.exists()) :
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()

if (ttyARDUINO.exists()) :
    arduino.write('0'.encode())
    arduino.close()

