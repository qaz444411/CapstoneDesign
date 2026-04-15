#! /usr/bin/env python3

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan

# Initialize the node
rospy.init_node('tutorial')

# Initialize publishers
publisher = rospy.Publisher('/YOLO', String, queue_size=10)
publisher2 = rospy.Publisher('/scan', LaserScan, queue_size=10)

# Initialize a rate object to control the publish rate
rate = rospy.Rate(5)

# Creating LaserScan object
laser = LaserScan()
laser.header.frame_id = 'laser'
laser.angle_min = -3.14  # rplidar provides a 360 degree field of view, so setting min angle as -180 degrees
laser.angle_max = 3.14  # Setting maximum angle as 180 degrees
laser.angle_increment = 3.14 / 180  # The angle increment for a 360 degree scan with 360 samples
laser.time_increment = (1.0 / 8000) / 360  # The time increment considering an 8000Hz sampling rate and 360 samples per scan
laser.scan_time = 1.0 / 5  # Considering that the publisher rate is 5Hz
laser.range_min = 0.15  # rplidar's minimum range is 15cm
laser.range_max = 12.0  # rplidar's maximum range is 12m

# Filling the ranges array with some random values
# Note that there are 360 points in a scan for this example
laser.ranges = [1.0]*360  

while not rospy.is_shutdown():
    publisher.publish('YOLO')
    laser.header.stamp = rospy.Time.now()  # Update the timestamp of the LaserScan message
    publisher2.publish(laser)
    rate.sleep()

