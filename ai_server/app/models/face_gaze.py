from typing import Dict, Optional, Tuple
rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
res = self._fm.process(rgb)
if not res.multi_face_landmarks: return None
lm = res.multi_face_landmarks[0]
h, w = face.shape[:2]
pts = [
self._p2d(lm, NOSE_TIP, w, h), self._p2d(lm, CHIN, w, h),
self._p2d(lm, LEFT_EYE_OUT, w, h), self._p2d(lm, RIGHT_EYE_OUT, w, h),
self._p2d(lm, MOUTH_L, w, h), self._p2d(lm, MOUTH_R, w, h),
]
if any(p is None for p in pts): return None
image_points = np.array(pts, dtype=np.float64)
# 간단한 3D 모델 (mm)
model_points = np.array([
[0.0, 0.0, 0.0], # nose tip
[0.0, -63.6, -12.5], # chin
[-43.3, 32.7, -26.0], # left eye outer
[43.3, 32.7, -26.0], # right eye outer
[-28.9, -28.9, -24.1], # left mouth
[28.9, -28.9, -24.1], # right mouth
])
focal = w
cam_matrix = np.array([[focal, 0, w/2],[0, focal, h/2],[0,0,1]], dtype=np.float64)
dist = np.zeros((4,1))
ok, rvec, tvec = cv2.solvePnP(model_points, image_points, cam_matrix, dist, flags=cv2.SOLVEPNP_ITERATIVE)
if not ok: return None
R, _ = cv2.Rodrigues(rvec)
sy = np.sqrt(R[0,0]**2 + R[1,0]**2)
pitch = float(np.degrees(np.arctan2(-R[2,0], sy))) # up/down
yaw = float(np.degrees(np.arctan2(R[1,0], R[0,0]))) # left/right
return yaw, pitch


def estimate(self, img: np.ndarray) -> Dict[str, object]:
self.load()
boxes = self.detector.detect(img)
if not boxes:
return {"direction": "unknown", "confidence": 0.0, "box": None}
b = max(boxes, key=lambda x: x["w"]*x["h"]) ; x,y,w,h = b["x"],b["y"],b["w"],b["h"]
face = img[y:y+h, x:x+w]
if face.size == 0:
return {"direction": "unknown", "confidence": 0.0, "box": b}
pose = self._pose(face)
if pose is None:
return {"direction": "center", "confidence": 0.3, "box": b}
yaw, pitch = pose
horiz = "left" if yaw < -15 else ("right" if yaw > 15 else "center")
vert = "up" if pitch < -10 else ("down" if pitch > 10 else "center")
direction = horiz if horiz != "center" else (vert if vert != "center" else "center")
conf = float(min(1.0, (abs(yaw)/30 + abs(pitch)/20)))
return {"direction": direction, "confidence": conf, "box": b}
