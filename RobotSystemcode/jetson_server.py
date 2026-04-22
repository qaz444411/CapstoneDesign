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
# 친구와 점수가 겹친다면 이 값을 조금씩 조절해보세요.
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

# [3] 기준 사진(지문) 특징 추출 (최초 1회만 수행)
# 파일 경로(str)를 리스트에 담아 전달합니다.
anchor_feature = extractor([ANCHOR_PATH])

# ==========================================
# [4] 카메라 루프 시작
# ==========================================
cap = cv2.VideoCapture(0) # 젯슨 NX 기본 카메라

print("\n" + "="*40)
print("   실시간 Re-ID 강인성 테스트 시작")
print("   (Q를 누르면 종료됩니다)")
print("="*40)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # [A] 탐색 영역(ROI) 설정 (화면 중앙 전신 영역)
    h, w, _ = frame.shape
    roi_w, roi_h = int(w * 0.4), int(h * 0.8)
    x1, y1 = (w - roi_w) // 2, (h - roi_h) // 2
    roi = frame[y1:y1+roi_h, x1:x1+roi_w]

    # [B] 특징 추출 (에러 해결: Numpy 배열을 직접 전달)
    # OpenCV의 BGR을 RGB로 변환한 후 리스트로 감싸서 전달합니다.
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    current_feature = extractor([roi_rgb])
    
    # [C] 코사인 유사도 계산
    similarity = F.cosine_similarity(anchor_feature, current_feature).item()

    # [D] 결과 판정 및 시각화
    # 임계값을 넘으면 초록색(MASTER), 아니면 빨간색(UNKNOWN)
    is_master = similarity > THRESHOLD
    color = (0, 255, 0) if is_master else (0, 0, 255)
    label = "MASTER" if is_master else "UNKNOWN"
    
    # 가이드 박스 및 정보 표시
    cv2.rectangle(frame, (x1, y1), (x1+roi_w, y1+roi_h), color, 3)
    cv2.rectangle(frame, (x1, y1-35), (x1+roi_w, y1), color, -1) # 라벨 배경
    cv2.putText(frame, f"{label}: {similarity:.3f}", (x1+5, y1-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 하단 유사도 게이지 바
    bar_x = int(similarity * w)
    cv2.rectangle(frame, (0, h-15), (bar_x, h), color, -1)

    # 화면 출력
    cv2.imshow("Physical 100 - Robustness Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n--- 테스트 종료 ---")