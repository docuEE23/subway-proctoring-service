from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # YOLOv8 weights (자동 다운로드 가능: yolov8n.pt)
    YOLO_WEIGHTS: str = "yolov8n.pt"
    # COCO 클래스명 기준 금지 물품
    BANNED_CLASSES: List[str] = ["cell phone", "book", "laptop", "tablet", "earphone", "headphones"]
    # 시선 이탈 임계값(도)
    GAZE_YAW_THRESHOLD: float = 25.0   # 좌우
    GAZE_PITCH_THRESHOLD: float = 20.0 # 상하
    # 자리 이탈(얼굴 미검출) 프레임 연속 임계
    ABSENT_CONSEC_FRAMES: int = 5
    # 알림 쿨다운(초)
    EVENT_COOLDOWN_SEC: float = 10.0

    CORS_ALLOW_ORIGINS: List[str] = ["*"]

settings = Settings()
