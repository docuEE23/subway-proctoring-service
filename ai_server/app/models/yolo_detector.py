from ultralytics import YOLO
import cv2
from typing import List, Tuple
from app.config import settings

class YoloDetector:
    def __init__(self, weights: str = None, classes: List[str] = None):
        self.model = YOLO(weights or settings.YOLO_WEIGHTS)
        self.names = self.model.model.names if hasattr(self.model, "model") else self.model.names
        self.banned = set((classes or settings.BANNED_CLASSES))
        # banned 중 실제 모델 클래스에 존재하는 것만 필터링
        self.valid_banned = {c for c in self.banned if c in self.names.values() or c in self.names}
    def detect_banned(self, img):
        res = self.model.predict(img, imgsz=640, conf=0.25, verbose=False)[0]
        events = []
        for b in res.boxes:
            cls_id = int(b.cls.item())
            cls_name = self.names[cls_id]
            if cls_name in self.valid_banned:
                events.append({
                    "cls": cls_name,
                    "conf": float(b.conf.item()),
                    "xyxy": [float(x) for x in b.xyxy[0].tolist()]
                })
        return events
