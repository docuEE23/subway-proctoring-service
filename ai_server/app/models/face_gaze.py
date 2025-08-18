import mediapipe as mp
import numpy as np
import cv2
from app.config import settings

# 간이 시선/존재 추정기:
# - 존재: 얼굴 랜드마크 검출 성공 여부
# - 시선: 양 눈/코 끝 기준으로 yaw/pitch 근사
#   (정밀한 PnP 기반 추정은 TODO로 두고 임계각 기반 간이판단)

class FaceGaze:
    def __init__(self):
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.absent_counter = 0

    def _estimate_angles(self, landmarks, img_w, img_h):
        # 33(코 끝), 263(우측 눈 바깥), 33? -> MediaPipe 인덱스 다수, 여기선 대표값 사용
        # landmarks: normalized (x,y,z)
        # 간이 yaw: 좌/우 눈 외곽 중심 대비 코 끝의 좌우 치우침
        left_idx = 33   # 왼 눈 외곽(근사)
        right_idx = 263 # 오른 눈 외곽(근사)
        nose_idx = 1    # 코 브릿지(근사)

        lx, ly = landmarks[left_idx].x * img_w, landmarks[left_idx].y * img_h
        rx, ry = landmarks[right_idx].x * img_w, landmarks[right_idx].y * img_h
        nx, ny = landmarks[nose_idx].x * img_w, landmarks[nose_idx].y * img_h

        eye_cx, eye_cy = (lx + rx) / 2.0, (ly + ry) / 2.0
        dx, dy = nx - eye_cx, ny - eye_cy

        # 픽셀 오프셋을 각도로 근사 (카메라 FoV 가정 60도)
        # 실제 환경에서는 solvePnP 등으로 교체 권장
        fov = 60.0
        norm_x = dx / (img_w / 2.0)  # -1 ~ 1
        norm_y = dy / (img_h / 2.0)
        yaw = norm_x * (fov / 2.0)
        pitch = norm_y * (fov / 2.0)
        return yaw, pitch

    def analyze(self, img):
        h, w = img.shape[:2]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = self.mesh.process(img_rgb)
        events = []
        face_present = False
        yaw = pitch = 0.0

        if res.multi_face_landmarks:
            face_present = True
            self.absent_counter = 0
            lm = res.multi_face_landmarks[0].landmark
            yaw, pitch = self._estimate_angles(lm, w, h)

            if (abs(yaw) >= settings.GAZE_YAW_THRESHOLD) or (abs(pitch) >= settings.GAZE_PITCH_THRESHOLD):
                events.append({
                    "type": "GAZE_AWAY",
                    "score": float(max(abs(yaw)/settings.GAZE_YAW_THRESHOLD,
                                       abs(pitch)/settings.GAZE_PITCH_THRESHOLD)),
                    "detail": {"yaw": yaw, "pitch": pitch}
                })
        else:
            self.absent_counter += 1
            if self.absent_counter >= settings.ABSENT_CONSEC_FRAMES:
                events.append({
                    "type": "ABSENT",
                    "score": 1.0,
                    "detail": {"consec_frames": self.absent_counter}
                })

        return events, face_present, yaw, pitch

    def close(self):
        # mediapipe 솔루션은 컨텍스트 내 자동 해제되지만, 명시적으로 처리
        pass
