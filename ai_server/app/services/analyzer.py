import time
from app.utils.image import read_image_from_bytes
from app.models.yolo_detector import YoloDetector
from app.models.face_gaze import FaceGaze
from app.schemas import AnalyzeResult, Detection
from app.config import settings

class Cooldown:
    def __init__(self, sec: float):
        self.sec = sec
        self.last = {}

    def allow(self, key: str):
        now = time.time()
        prev = self.last.get(key, 0)
        if now - prev >= self.sec:
            self.last[key] = now
            return True
        return False

class Analyzer:
    def __init__(self):
        self.detector = YoloDetector()
        self.gaze = FaceGaze()
        self.cooldown = Cooldown(settings.EVENT_COOLDOWN_SEC)

    def analyze_bytes(self, img_bytes: bytes) -> AnalyzeResult:
        t0 = time.time()
        img = read_image_from_bytes(img_bytes)

        out_events = []

        # 1) 얼굴 존재 & 시선
        gaze_events, face_present, yaw, pitch = self.gaze.analyze(img)
        for e in gaze_events:
            if self.cooldown.allow(e["type"]):
                out_events.append(Detection(
                    type="GAZE_AWAY",
                    score=e["score"],
                    detail=e.get("detail"),
                    ts=time.time()
                ))
        if not face_present and self.cooldown.allow("ABSENT"):
            out_events.append(Detection(type="ABSENT", score=1.0, detail=None, ts=time.time()))

        # 2) 금지 물품 탐지 (YOLO)
        banned = self.detector.detect_banned(img)
        for b in banned:
            key = f"BANNED_OBJECT:{b['cls']}"
            if self.cooldown.allow(key):
                out_events.append(Detection(
                    type="BANNED_OBJECT",
                    score=b["conf"],
                    detail={"cls": b["cls"], "bbox": b["xyxy"]},
                    ts=time.time()
                ))

        return AnalyzeResult(
            events=out_events,
            latency_ms=int((time.time() - t0) * 1000)
        )

    def close(self):
        self.gaze.close()
