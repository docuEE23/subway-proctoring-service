from typing import Optional
self._fm = _mp_fm.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
if self._sess is None:
settings = get_settings()
path = settings.face_embedder_path
if os.path.exists(path):
providers = ["CPUExecutionProvider"]
self._sess = ort.InferenceSession(path, providers=providers)
self._input_name = self._sess.get_inputs()[0].name
self.detector.load()


# --- alignment helpers ---
def _align_by_eyes(self, img: np.ndarray) -> Optional[np.ndarray]:
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
res = self._fm.process(rgb)
if not res.multi_face_landmarks:
return None
lm = res.multi_face_landmarks[0]; h, w = img.shape[:2]
try:
pL = lm.landmark[LEFT_EYE]; pR = lm.landmark[RIGHT_EYE]
except Exception:
return None
xL, yL = int(pL.x*w), int(pL.y*h); xR, yR = int(pR.x*w), int(pR.y*h)
# 표준 ArcFace 정렬 프레임 (112x112에서 눈 위치)
tgtL, tgtR = (38, 38), (74, 38)
src = np.float32([[xL, yL], [xR, yR], [xL, yL+40]])
dst = np.float32([[tgtL[0], tgtL[1]], [tgtR[0], tgtR[1]], [tgtL[0], tgtL[1]+40]])
M = cv2.getAffineTransform(src, dst)
return cv2.warpAffine(img, M, (112, 112), flags=cv2.INTER_CUBIC)


def _crop_fallback(self, img: np.ndarray) -> Optional[np.ndarray]:
boxes = self.detector.detect(img)
if not boxes: return None
b = max(boxes, key=lambda x: x["w"]*x["h"]) ; x,y,w,h = b["x"],b["y"],b["w"],b["h"]
face = img[y:y+h, x:x+w]
if face.size == 0: return None
return cv2.resize(face, (112,112), interpolation=cv2.INTER_AREA)


def _preprocess_arcface(self, img112: np.ndarray) -> np.ndarray:
rgb = cv2.cvtColor(img112, cv2.COLOR_BGR2RGB)
x = rgb.astype(np.float32) / 255.0
x = (x - 0.5) / 0.5 # [-1,1]
x = np.transpose(x, (2,0,1))[None, ...] # NCHW
return x.astype(np.float32)


def _embed_onnx(self, img112: np.ndarray) -> Optional[np.ndarray]:
if self._sess is None: return None
inp = self._preprocess_arcface(img112)
feat = self._sess.run(None, {self._input_name: inp})[0]
v = feat.reshape(-1).astype(np.float32)
v /= (np.linalg.norm(v) + 1e-8)
return v


def _embed_fallback(self, img112: np.ndarray) -> np.ndarray:
gray = cv2.cvtColor(img112, cv2.COLOR_BGR2GRAY)
v = cv2.resize(gray, (64,64), interpolation=cv2.INTER_AREA).astype(np.float32).reshape(-1)
v = (v - v.mean()) / (v.std()+1e-6)
v /= (np.linalg.norm(v)+1e-8)
return v


def _embed(self, img: np.ndarray) -> Optional[np.ndarray]:
self.load()
aligned = self._align_by_eyes(img) or self._crop_fallback(img)
if aligned is None: return None
v = self._embed_onnx(aligned)
if v is None: # 가중치가 없으면 폴백
v = self._embed_fallback(aligned)
return v


def verify(self, img_probe: np.ndarray, img_ref: np.ndarray) -> Optional[float]:
e1 = self._embed(img_probe); e2 = self._embed(img_ref)
if e1 is None or e2 is None: return None
return float(np.dot(e1, e2) / (np.linalg.norm(e1)*np.linalg.norm(e2)+1e-8))
