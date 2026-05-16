import cv2
import torch
import serial
import numpy as np
from ultralytics import YOLO
from torchreid.utils import FeatureExtractor
import torch.nn.functional as F
import time
import os
import socketio
import requests
import warnings
warnings.filterwarnings("ignore")

# ============================================================
#  [1] 설정값
# ============================================================

SERVER_URL  = 'http://100.81.96.26:3001'
MODEL_PATH  = '/media/meta3/UBUNTU 20_0/reid_results_final/model/model.pth.tar-120'
SERIAL_PORT = '/dev/ttyUSB_DRV0'

THRESHOLD       = 0.72
STEER_CENTER    = 90
STOP_THROTTLE   = 90
MIN_DRIVE_POWER = 105
IMAGE_WIDTH     = 640

# ============================================================
#  [2] 전역 상태
# ============================================================

is_running     = False
master_feature = None
user_token     = None   # 앱에서 전달받은 JWT 토큰

# ============================================================
#  [3] 하드웨어 초기화
# ============================================================

print("--- 시스템 초기화 중 ---")

try:
    ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
    print("✅ 아두이노 연결 성공")
except Exception as e:
    print(f"⚠️  시리얼 연결 실패: {e}")
    ser = None

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"✅ 디바이스: {device}")

yolo = YOLO('yolo11n.pt')
print("✅ YOLO 로드 완료")

reid_extractor = FeatureExtractor(
    model_name='osnet_ain_x1_0',
    model_path=MODEL_PATH,
    device=device
)
print("✅ Re-ID 모델 로드 완료")

# ============================================================
#  [4] 아두이노 명령 전송
# ============================================================

def send_to_arduino(steer, throttle):
    steer    = max(65, min(115, steer))
    throttle = max(85, min(120, throttle))
    if ser:
        ser.write(f"{steer},{throttle}\n".encode())

# ============================================================
#  [5] Socket.io 설정
# ============================================================

sio = socketio.Client(reconnection=True, reconnection_attempts=0)

@sio.event
def connect():
    print("✅ 서버 소켓 연결 성공")
    sio.emit('jetson_register', {})

@sio.event
def disconnect():
    print("⚠️  서버 소켓 연결 끊김 — 재연결 중...")
    send_to_arduino(STEER_CENTER, STOP_THROTTLE)

# ============================================================
#  [6] 서버 → 잿슨 명령 수신 (START / STOP)
# ============================================================

@sio.on('server_to_jetson')
def on_command(data):
    global is_running, master_feature, user_token

    # ✅ 딕셔너리에서 command, token 꺼내기
    cmd   = data.get('command')
    token = data.get('token')

    if token:
        user_token = token

    print(f"\n📱 명령 수신: {cmd}")

    if cmd == 'START':
        if not user_token:
            print("❌ 토큰 없음 — 앱에서 로그인 후 다시 시도하세요")
            return
        try:
            headers = {'Authorization': f'Bearer {user_token}'}
            res = requests.get(
                f"{SERVER_URL}/api/owner/data",
                headers=headers,
                timeout=5
            )
            if res.status_code == 200:
                desc_list = res.json()['descriptor']

                # 리스트 → [1, 512] 텐서 변환 후 L2 정규화
                master_feature = torch.tensor(
                    desc_list, dtype=torch.float32, device=device
                ).unsqueeze(0)
                master_feature = F.normalize(master_feature, p=2, dim=1)

                is_running = True
                print("🎯 마스터 특징벡터 장착 완료! 추종 시작")

            elif res.status_code == 404:
                print("❌ 등록된 특징벡터 없음 — 앱에서 사진을 먼저 업로드하세요")
                sio.emit('jetson_to_server', {'status': 'ERROR: 타겟 미등록', 'target': 'None'})

            elif res.status_code == 403:
                print("❌ 토큰 인증 실패 (403) — 앱에서 다시 로그인하세요")

            else:
                print(f"❌ 서버 응답 오류: {res.status_code}")

        except requests.exceptions.ConnectionError:
            print("❌ 서버 연결 실패")
        except Exception as e:
            print(f"❌ START 처리 오류: {e}")

    elif cmd == 'STOP':
        is_running     = False
        master_feature = None
        send_to_arduino(STEER_CENTER, STOP_THROTTLE)
        print("🛑 정지 완료")

# ============================================================
#  [7] 수동 조종 명령 수신
# ============================================================

@sio.on('manual_control')
def on_manual(data):
    if not is_running:
        steer    = data.get('steer',    STEER_CENTER)
        throttle = data.get('throttle', STOP_THROTTLE)
        send_to_arduino(steer, throttle)

# ============================================================
#  [8] 카메라 초기화
# ============================================================

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_count = 0

print("\n" + "="*45)
print("   PHYSICAL 100 — 추종 시스템 대기 중")
print("   웹 앱에서 START 버튼을 누르세요")
print("="*45 + "\n")

# ============================================================
#  [9] 메인 루프
# ============================================================

try:
    sio.connect(SERVER_URL)

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        # 대기 상태
        if not is_running or master_feature is None:
            send_to_arduino(STEER_CENTER, STOP_THROTTLE)
            cv2.putText(frame, "WAITING FOR COMMAND", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("Physical 100 - Tracking", frame)
            sio.emit('jetson_to_server', {
                'status':    'WAITING',
                'target':    'None',
                'steer':     STEER_CENTER,
                'throttle':  STOP_THROTTLE,
                'similarity': None
            })
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # 추종 모드 — 2프레임당 1번 추론
        frame_count += 1
        if frame_count % 2 != 0:
            cv2.imshow("Physical 100 - Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # A. YOLO 사람 검출
        results    = yolo(frame, classes=[0], verbose=False)
        best_sim   = -1
        target_box = None

        for r in results:
            for box in r.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)
                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    continue

                # B. Re-ID 유사도 계산
                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                feat     = reid_extractor([crop_rgb])
                feat     = F.normalize(feat, p=2, dim=1)
                sim      = F.cosine_similarity(master_feature, feat).item()

                if sim > THRESHOLD and sim > best_sim:
                    best_sim   = sim
                    target_box = (x1, y1, x2, y2)

        # C. 주행 제어
        current_steer    = STEER_CENTER
        current_throttle = STOP_THROTTLE
        status_msg       = 'LOST MASTER'

        if target_box:
            x1, y1, x2, y2 = target_box
            cx = (x1 + x2) / 2
            h  = y2 - y1

            error_x       = cx - (IMAGE_WIDTH / 2)
            current_steer = int(STEER_CENTER + error_x * 0.1)
            current_steer = max(65, min(115, current_steer))

            if h < 350:
                current_throttle = MIN_DRIVE_POWER
                status_msg       = f"MOVING (sim:{best_sim:.2f})"
            else:
                current_throttle = STOP_THROTTLE
                status_msg       = "STOP (TOO CLOSE)"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, f"MASTER {best_sim:.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            print(f"\r[추종] sim:{best_sim:.2f} | 조향:{current_steer} | 스로틀:{current_throttle}   ", end="")
        else:
            print(f"\r[탐색] 마스터 미검출...   ", end="")

        # D. 아두이노 + 서버 전송
        send_to_arduino(current_steer, current_throttle)
        sio.emit('jetson_to_server', {
            'status':     status_msg,
            'target':     'MASTER' if target_box else 'None',
            'steer':      current_steer,
            'throttle':   current_throttle,
            'similarity': round(best_sim, 4) if best_sim > 0 else None
        })

        fps = 1.0 / (time.time() - start_time + 1e-6)
        cv2.putText(frame, f"FPS:{fps:.1f} | {status_msg}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Physical 100 - Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ============================================================
#  [10] 종료 처리
# ============================================================

finally:
    print("\n\n--- 시스템 종료 중 ---")
    send_to_arduino(STEER_CENTER, STOP_THROTTLE)
    if ser:
        ser.close()
    sio.disconnect()
    cap.release()
    cv2.destroyAllWindows()
    print("--- 종료 완료 ---")
