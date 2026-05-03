import cv2
import torch
import torch.nn.functional as F
from torchreid.utils import FeatureExtractor
import numpy as np
import os





# ==========================================
# [1] 경로 및 임계값 설정
# ==========================================
BASE_PATH = '/media/meta3/UBUNTU 20_0/reid_results_final'
MODEL_PATH = os.path.join(BASE_PATH, 'model/model.pth.tar-120')
ANCHOR_PATH = os.path.join(BASE_PATH, 'data/real_my_anchor.png')

# 120 에포크 결과(0.8069)를 고려해 0.75를 기준으로 잡습니다.
THRESHOLD = 0.75 

print(f"--- 모델 로드 중: {MODEL_PATH} ---")

# ==========================================
# [2] Re-ID 모델 초기화 (CUDA 사용)
# ==========================================
extractor = FeatureExtractor(
    model_name='osnet_ain_x1_0',
    model_path=MODEL_PATH,
    device='cuda'
)

# 앵커 이미지 존재 여부 확인 후 특징 추출
if not os.path.exists(ANCHOR_PATH):
    raise FileNotFoundError(f"앵커 이미지를 찾을 수 없습니다: {ANCHOR_PATH}")

# 최초 1회 특징 추출 시에도 no_grad 적용
with torch.no_grad():
    anchor_feature = extractor([ANCHOR_PATH])

# ==========================================
# [4] 카메라 루프 시작
# ==========================================
cap = cv2.VideoCapture(0) # 젯슨 NX 기본 웹캠 (CSI 카메라인 경우 gstreamer 파이프라인 필요할 수 있음)

if not cap.isOpened():
    print("에러: 카메라를 열 수 없습니다.")
    exit()

print("\n" + "="*40)
print("   실시간 Re-ID 강인성 테스트 시작")
print("   (Q를 누르면 종료됩니다)")
print("="*40)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라 프레임을 읽어오지 못했습니다.")
        break

    # [A] 탐색 영역(ROI) 설정 (화면 중앙 전신 영역)
    h, w, _ = frame.shape
    roi_w, roi_h = int(w * 0.4), int(h * 0.8)
    x1, y1 = (w - roi_w) // 2, (h - roi_h) // 2
    roi = frame[y1:y1+roi_h, x1:x1+roi_w]

    # ROI 영역이 유효한지 검증 (크기가 0이 아닌지)
    if roi.size == 0:
        continue

    # [B] 특징 추출 (메모리 확보 및 연산 속도 향상을 위해 no_grad 선언)
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    
    with torch.no_grad():
        current_feature = extractor([roi_rgb])
        # [C] 코사인 유사도 계산
        similarity = F.cosine_similarity(anchor_feature, current_feature).item()

    # 음수 방지 및 값 제한
    similarity = max(0.0, min(1.0, similarity))

    # [D] 결과 판정 및 시각화
    is_master = similarity > THRESHOLD
    color = (0, 255, 0) if is_master else (0, 0, 255)
    label = "MASTER" if is_master else "UNKNOWN"
    
    # 가이드 박스