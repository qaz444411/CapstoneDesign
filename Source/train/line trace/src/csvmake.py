# -*- coding: utf-8 -*-
"""
Created on 16:19:31 20 Dec 2022 by the Mr. JaeGun Song workin HUINS.

"""

import os
import csv

center_image_path = 'D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/center/'
center_img_list = os.listdir(center_image_path) #디렉토리 내 모든 파일 불러오기
center_img_list_jpg = [img for img in center_img_list if img.endswith(".jpg")] #지정된 확장자만 필터링

left_image_path = 'D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/left/'
left_img_list = os.listdir(left_image_path) 
left_img_list_jpg = [img for img in left_img_list if img.endswith(".jpg")] 

right_image_path = 'D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/right/'
right_img_list = os.listdir(right_image_path) 
right_img_list_jpg = [img for img in right_img_list if img.endswith(".jpg")]

# 각각의 파일 이름을 저장한 driving_log.csv파일 생성. 
with open('D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/driving_log.csv', 'w', newline='', encoding = 'UTF-8') as csvfile:
    # Create a CSV writer
    writer = csv.writer(csvfile)

    #Write the column headers
    #writer.writerow(['Center Image', 'Left Image', 'Right Image'])

    # Zip the lists of image names together and write them to the CSV file
    for center, left, right in zip(center_img_list_jpg, left_img_list_jpg, right_img_list_jpg):
        center_name = 'dataset\\' + center
        left_name = 'dataset\\' + left
        right_name = 'dataset\\' + right
        writer.writerow([center_name, left_name, right_name])

# 생성된 steering_angle.txt 파일안의 내용을 전부 복사하여 같이 만들어진 driving_log.csv 파일의 이미지이름들 다음 4번째 열에 넣어준다.
f = open("D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/AI_20221220.txt", 'r', encoding='UTF-8') 
lines = f.readlines()   #촬영할 때 저장된 조향각 데이터를 읽어온다. 
for line in lines:
    line = line.split("\n") 
    line = line[-2] 
    if line[-3] == ":":      #조향각이 105, 110과 같이 3자리 값이 있어서, 2자리 앞에 ':45', ':97' 붙는 것들은 걸러준다.
        steer = int(line[-2] + line[-1])
    else:
        steer = int(line[-3] + line[-2] + line [-1])    
    steering = int(steer)    #조향각을 값을 비교하고 수정하기 위해 정수형으로 변환해준다.
    
    #걸러준 조향각을 학습에 맞는 조향값으로 변환해준다. 차선학습에 맞는 조향값은 직진이 0, 좌회전 1, 우회전 -1 이다.     
    if steering >= 75 and steering < 105:
        steering_angle = 0        
    elif steering >= 35 and steering < 75:
        steering_angle = 1
    elif steering >= 105 and steering < 145:
        steering_angle = -1
        
    w = str(steering_angle)   #파일에 저장하기 위해 정수를 문자열로 변환해준다.
    file = open("D:/Huins/EDU Platform/교육/CAR2/train/line trace/dataset/steering_angle.txt", 'at')
    file.write(w + '\n')
    file.close()
f.close()   


