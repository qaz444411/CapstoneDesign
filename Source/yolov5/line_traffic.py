#필요한 패키지.모듈.함수 불러오기. 
#파이썬 코드는 임포팅 이라는 프로세스를 통해 다른 패키지나 모듈 혹은 (내장.외장)함수에 있는 코드들에 대한 접근권을 얻습니다.
import rospy
import torch
import torch.backends.cudnn as cudnn
import numpy as np
import cv2
import math
import matplotlib
import torchvision.transforms as transforms
import time

from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from models.common import DetectMultiBackend
from utils.datasets import LoadStreams
from utils.general import (check_img_size, check_imshow, check_requirements, non_max_suppression)
from utils.torch_utils import select_device

from model import NetworkNvidia
from torch.autograd import Variable
from serial import Serial

ser = Serial('/dev/arduino',115200,timeout=1) 
#터미널 창에서 'ls /dev/tty*'로 아두이노 보드와 연결된 USB가 몇번으로 잡혀있는지 확인해주어야 한다.

transformations = transforms.Compose([transforms.Lambda(lambda x: (x / 127.5) - 1.0)])
#데이터가 항상 머신러닝 알고리즘 학습에 필요한 최종 처리가 된 형태로 제공되지는 않습니다. 변형(transform)을 해서 데이터를 조작하고 학습에 적합하게 만듭니다.

motor_flag = 0  #모터 초기화

@torch.no_grad() #gradient(경사)은 사용하지 않도록 설정함으로서, 필요한 메모리를 줄여주고 연산속도를 높인다.

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

def img2ten(im0s): #영상 이미지 설정 
    image_array = np.array(im0s[0])
    image_array = cv2.resize(image_array, (320, 180))
    image_array = image_array[-70:, :, :]

    # transform RGB to BGR for cv2
    image_array = image_array[:, :, ::-1]
    image_array = transformations(image_array)
    image_tensor = torch.Tensor(image_array)
    image_tensor = image_tensor.view(1, 3, 70, 320)
    image_tensor = Variable(image_tensor)
    return image_tensor

def yolov5_call(var):
    
    print ('--------------------------excute yolov5_call_function')
    global motor_flag
 
  #학습된 파일 설정: 학습시킨 파일의 경로와 파일이름을 여기에 써준다. 
    model_H='/home/huins/yolov5/line_trace_cnn_best.h5' 
    weights='/home/huins/yolov5/yolov5_traffic.pt' 
    data='/home/huins/yolov5/data/traffic.yaml'  # dataset.yaml path
    
    source=str(0)
    imgsz=(640, 640)  # inference size (height, width)
    conf_thres=0.25  # confidence threshold
    iou_thres=0.45  # NMS IOU threshold
    max_det=100  # maximum detections per image
    device='0'  # cuda device, i.e. 0 or 0,1,2,3 or cpu
    classes=None  # filter by class: --class 0, or --class 0 2 3
    agnostic_nms=False  # class-agnostic NMS
    augment=False  # augmented inference
    visualize=False  # visualize features
    half=False  # use FP16 half-precision inference
    dnn=False  # use OpenCV DNN for ONNX inference
    webcam = source.isnumeric()
    
    #웹캠(카메라)의 동작일 때와 아닐 때(이미지, 동영상)의 dataset 설정
    # Load model 
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data)
    stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    
    #모터 초기 조향값, 모터값 설정
    strval = 0x5A
    spdval = 0x61
    
    # Half
    half &= (pt or jit or onnx or engine) and device.type != 'cpu'  # FP16 supported on limited backends with CUDA
    if pt or jit:
        model.model.half() if half else model.model.float()
 
    # Dataloader: 웹캠(카메라)로 보여지는 이미지들을 읽고 데이터셋을 로드한다.
    if webcam:
        view_img = True#check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
    dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
 
    # Run inference: 설정된 source, model, dataset을 기반으로 detect 동작 수행. 동영상이나 카메라일 경우 매 frame마다 연속적으로 동작하고, 사진이면 사진 한 장의 결과 값을 보여준다.
    model.warmup(imgsz=(1, 3, *imgsz), half=half)  # warmup
    for path, im, im0s, vid_cap, s in dataset:
 
    #Steering 추론에 따른 주행을 위한 모터 제어
        model2 = NetworkNvidia()
        # check that model version is same as local PyTorch version
        try:
            checkpoint = torch.load(model_H, map_location=lambda storage, loc: storage)
            model2.load_state_dict(checkpoint['state_dict'])
            
        except KeyError:
            checkpoint = torch.load(model_H, map_location=lambda storage, loc: storage)
            model2 = checkpoint['model']
                
        image_tensor = img2ten(im0s)
    
        steering_angle = model2(image_tensor).view(-1).data.numpy()[0]
        if abs(steering_angle) < 0.3:
            steering_angle = 0
        elif abs(steering_angle) > 2:
            print('steering_angle > 2')
            #ser.write('0'.encode())
        
        if (steering_angle > 0.5 and motor_flag == 0):
            steer = "Left"
            steering_angle = 45
            time.sleep(0.01)
            strval = 0x2D
            ser.write(create_command(strval, spdval))
        elif (steering_angle < -0.5 and motor_flag == 0) :
            steer = "Right"
            steering_angle = 135
            time.sleep(0.01)
            strval = 0x87
            ser.write(create_command(strval, spdval))
        elif (steering_angle == 0 and motor_flag == 0):
            steer = "Go"
            steering_angle = 90
            strval = 0x5A
            ser.write(create_command(strval, spdval))
            time.sleep(0.01)
 
        steer_angle = steer + '(' + format(steering_angle, '.02f') + ')'
        print(steer)
        #print(steer_angle)
        
        
    # Traffic
        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
 
        # Inference 학습된 신호등에 대한 추론
        pred = model(im, augment=augment, visualize=visualize)
 
        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
 
        # Process predictions 예측 실행
        for i, det in enumerate(pred):  # per image
            if len(det):
                for c in det[:, -1].unique():
                    label = names[int(c)]
                    
                    if label=='green':   #녹색불
                        print("I see green light")
                        motor_flag = 0
                        ser.write(create_command(strval, spdval))
                        time.sleep(0.2)
                    elif label=='red':   #빨간불
                        print("Red light")
                        motor_flag = 1
                        ser.write(create_command(strval, 0x00))
                        time.sleep(0.2)
                                            
                    elif label=='40_sign':   # 40 표지판
                        print("40 Speed sign")
                        motor_flag = 0
                        spdval = 0x60
                        ser.write(create_command(strval, spdval))
                        time.sleep(0.2)                   
                    elif label=='80_sign':   # 80 표지판
                        print("80 Speed sign")
                        motor_flag = 0
                        spdval = 0x62
                        ser.write(create_command(strval, spdval))
                        time.sleep(0.2)
                        
                    elif label=='stop_sign':   # 정지 표지판
                        print("Stop sign")
                        motor_flag = 1
                        ser.write(create_command(strval, 0x00))
                        time.sleep(0.2)                   
                    elif label=='start_sign':   # 출발 표지판
                        print("Start sign")
                        motor_flag = 0
                        ser.write(create_command(strval, spdval))
                        time.sleep(0.2)
                    elif label=='person':       # 보행자
                        print("Obstacle : Person")
                        motor_flag = 1
                        ser.write(create_command(strval, 0x00))
                        time.sleep(0.2)


# 노드 정의
#‘YOLO’이라는 이름의 Subscriber를 만들고 ‘/YOLO’이라는 이름의 String 타입 메시지가 전달될 경우,"traffic_light"함수를 실행시킨다.
def laser_listener():
    rospy.init_node('laser_listener', anonymous=True)
    #rospy.init_node('NAME'): 이것은 rospy에게 노드의 이름을 알려주는 것이다. 
    #publisher 노드나 subscriber 노드나 어떤 노드를 선언할때는 초기에 이름을 지정해주어야한다. rospy가 이 정보를 얻기전까지는 ROS Master와 통신은 시작되지 않는다.
    
    check_requirements(exclude=('tensorboard', 'thop'))  
    sub = rospy.Subscriber('/YOLO', String, yolov5_call)
    rospy.spin()    #spin()함수는 ROS 노드가 shutdown 될 때까지 Block 하는 함수. 즉, 계속 실행 상태를 유지하라는 함수이다. 

if __name__ == '__main__':  #이 파일을 메인으로 실행한다는 뜻. 다른곳에서 실행되는 것을 막아준다.
    laser_listener()
