from typing import List, Dict
import cv2, numpy as np, mediapipe as mp


_mp_fd = mp.solutions.face_detection


class FaceDetector:
def __init__(self, min_conf: float = 0.6, model_selection: int = 0) -> None:
self.min_conf = min_conf
self.model_selection = model_selection
self._fd = None


def load(self) -> None:
if self._fd is None:
self._fd = _mp_fd.FaceDetection(model_selection=self.model_selection, min_detection_confidence=self.min_conf)


def detect(self, img: np.ndarray) -> List[Dict[str, float]]:
self.load(); h, w = img.shape[:2]
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
res = self._fd.process(rgb)
out: List[Dict[str, float]] = []
if not res.detections: return out
for det in res.detections:
r = det.location_data.relative_bounding_box
x1 = int(max(0, r.xmin) * w); y1 = int(max(0, r.ymin) * h)
x2 = int(min(1.0, r.xmin + r.width) * w); y2 = int(min(1.0, r.ymin + r.height) * h)
out.append({"x": x1, "y": y1, "w": max(0, x2-x1), "h": max(0, y2-y1), "score": float(det.score[0] if det.score else 0.0)})
return out
