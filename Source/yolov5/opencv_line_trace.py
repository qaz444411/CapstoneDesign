import cv2
import numpy as np
import argparse
import time
from serial import Serial

ser = Serial('/dev/arduino',115200,timeout=1)
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
    #print(Checksum)

    # Create the command bytearray
    command = bytearray([STX, Length, steering, speed, dummy1, dummy2, Checksum, ETX])

    return command


def main(source=0):
    camera = cv2.VideoCapture(source)
    camera.set(3, 640)
    camera.set(4, 480)
    
    strval = 0x5A # steering angle : 90
    spdval = 0x00 # speed value : 0
    
    while(camera.isOpened()):
        ret, frame = camera.read()
        cv2.imshow('normal', frame)
       
        crop_img = frame[360:,150:490]
       
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        ret, thresh1 = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
        
        mask = cv2.erode(thresh1, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow('mask', mask)
        
        # Find and draw object contours
        contours, hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
        
        if len(contours) > 0:

            # Calculate the background moments
            mask_inverse = cv2.bitwise_not(mask)  # Invert the mask to select the background
            background_moments = cv2.moments(mask_inverse)
            if background_moments['m00'] <= 0:
                print("Not found track")
                spdval = 0x30 # speed value : 0
                ser.write(create_command(strval, spdval))
            if background_moments['m10'] <= 0:
                print("Not found track")
                spdval = 0x30 # speed value : 0
                ser.write(create_command(strval, spdval))
                
            else :
                # Calculate and display the center of the background
                background_center_x = int(background_moments['m10'] / background_moments['m00']/340*180)
                background_center_y = int(background_moments['m01'] / background_moments['m00'])
                cv2.circle(frame, (background_center_x, background_center_y), 5, (0, 255, 0), -1)
                print(f"Background center: {background_center_x}")
                # Go Straight
                if (85 <= background_center_x <= 95):
                    strval = 0x5A # steering angle : 90
                    spdval = 0x61 # speed value : 97
                    ser.write(create_command(strval, spdval))
                # Tracking Trace
                if (45 <= background_center_x < 85 or 95 < background_center_x <= 135):
                    strval = hex(background_center_x)   # steering angle : background_center_x
                    spdval = 0x61                       # speed value : 97
                    ser.write(create_command(strval, spdval))
                # Trun Left
                if (background_center_x < 45): 
                    strval = 0x2D # steering angle : 45
                    spdval = 0x61 # speed value : 97
                    ser.write(create_command(strval, spdval))
                # Turn Right
                if (background_center_x > 135):
                    strval = 0x87 # steering angle : 135
                    spdval = 0x61 # speed value : 97
                    ser.write(create_command(strval, spdval))
            
                    
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process video source.')
    parser.add_argument('--source', type=int, default=0, help='Camera source (default: 0)')
    args = parser.parse_args()
    main(source=args.source)
