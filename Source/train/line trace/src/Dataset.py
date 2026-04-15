# -*- coding: utf-8 -*-
"""
Created on 16:19:31 20 Dec 2022 by the Mr. JaeGun Song workin HUINS.

"""

import os
from PIL import Image

image_path = './test/'

img_list = os.listdir(image_path) #디렉토리 내 모든 파일 불러오기
img_list_jpg = [img for img in img_list if img.endswith(".jpg")] #지정된 확장자만 필터링

for i in img_list_jpg:
    img = Image.open(image_path + i)
    img_resize = img.resize((411, 231), Image.LANCZOS)
    title, ext = os.path.splitext(i)
    img_resize.save('../dataset/resize/' + title + ext)
    
