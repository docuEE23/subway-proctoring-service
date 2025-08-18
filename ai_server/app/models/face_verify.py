import base64
import numpy as np
import cv2
from deepface import DeepFace
from app.schemas import FaceVerifyRequest, FaceVerifyResult

def _b64_to_img(b64: str):
    arr = np.frombuffer(base64.b64decode(b64), np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

class FaceVerifier:
    def __init__(self):
        # DeepFace는 최초 호출 시 모델 로드
        self.model_cache = {}

    def verify(self, req: FaceVerifyRequest) -> FaceVerifyResult:
        img1 = _b64_to_img(req.selfie_b64)
        img2 = _b64_to_img(req.idface_b64)

        # DeepFace.verify는 파일 경로나 numpy BGR도 허용
        obj = DeepFace.verify(img1, img2, model_name=req.model, enforce_detection=True)
        return FaceVerifyResult(
            is_match=bool(obj.get("verified", False)),
            distance=float(obj.get("distance", 0.0)),
            threshold=float(obj.get("threshold", 0.0)),
            model=req.model
        )

    def close(self):
        pass
