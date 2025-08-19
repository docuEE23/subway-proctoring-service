import base64, cv2, numpy as np
from typing import Dict, Any


from ..utils.config import get_settings
from ..utils.rtsp import grab_frame
from ..models.yolo_detector import FaceDetector
from ..models.face_verify import FaceVerifier
from ..models.face_gaze import GazeEstimator




def _b64_to_ndarray(data: str) -> np.ndarray:
raw = base64.b64decode(data)
arr = np.frombuffer(raw, dtype=np.uint8)
img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
if img is None: raise ValueError("Invalid image base64")
return img


class Analyzer:
def __init__(self) -> None:
self.settings = get_settings()
self.detector = FaceDetector(); self.verifier = FaceVerifier(); self.gazer = GazeEstimator()


def preload(self) -> None:
self.detector.load(); self.verifier.load(); self.gazer.load()


# Image APIs
def detect(self, image_b64: str) -> Dict[str, Any]:
img = _b64_to_ndarray(image_b64)
boxes = self.detector.detect(img)
return {"count": len(boxes), "boxes": boxes}


def verify(self, probe_b64: str, ref_b64: str) -> Dict[str, Any]:
img_p = _b64_to_ndarray(probe_b64)
img_r = _b64_to_ndarray(ref_b64)
sim = self.verifier.verify(img_p, img_r)
if sim is None: return {"similarity": 0.0, "is_match": False}
return {"similarity": float(sim), "is_match": bool(sim >= self.settings.face_verify_threshold)}


def gaze(self, image_b64: str) -> Dict[str, Any]:
img = _b64_to_ndarray(image_b64)
return self.gazer.estimate(img)


# RTSP APIs – single frame
def detect_rtsp(self, rtsp_url: str) -> Dict[str, Any]:
frame = grab_frame(rtsp_url)
boxes = self.detector.detect(frame)
return {"count": len(boxes), "boxes": boxes}


def gaze_rtsp(self, rtsp_url: str) -> Dict[str, Any]:
frame = grab_frame(rtsp_url)
return self.gazer.estimate(frame)
