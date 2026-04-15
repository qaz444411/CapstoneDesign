import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import time
from serial import Serial
from rplidar import RPLidar

ser = Serial('/dev/arduino',115200,timeout=1) 
#ser = Serial('/dev/ttyUSB1',115200,timeout=1) 
time.sleep(3)

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


def obstacle(data): 

    strval = 0x5A
    spdval = 0x00

    for i in range(len(data.ranges)):
        angle = (data.angle_min + i * data.angle_increment)*180/3.14 
        distance = data.ranges[i]*100
        
        if distance == float('inf'):
            continue
        

        # Stop
        if (-181.0 < angle < -177.0 or 177.0 < angle < 181.0) :
            if (distance > 50):
              print ("Obstacle : Go")
              print ("\n")
              strval = 0x5A
              spdval = 0x61
              ser.write(create_command(strval, spdval))
            else :
              print ("Obstacle : Frontal")
              print ("\n")
              spdval = 0x00
              ser.write(create_command(strval, spdval))
              continue


        # Obstacle : Left (turn Right)        
        if (-130.0 < angle <  -70.0):
            if (distance < 50) :
                print ("Obstacle : Left")
                print ("\n")
                strval = 0x87
                spdval = 0x61
                ser.write(create_command(strval, spdval))
                
        # Obstacle : Right (turn Left)      
        if (70.0 < angle < 130.0):
            if (distance < 50) :
                print ("Obstacle : Right")
                print ("\n")
                strval = 0x2D
                spdval = 0x61
                ser.write(create_command(strval, spdval))
                

                
    
def laser_listener():
    rospy.init_node('laser_listener', anonymous=True)
    rsub = rospy.Subscriber('/scan', LaserScan, obstacle, queue_size=1)
       
    rospy.spin()    

if __name__ == '__main__': 
    laser_listener()
