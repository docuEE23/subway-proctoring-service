from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Detection(BaseModel):
    type: Literal["BANNED_OBJECT", "GAZE_AWAY", "ABSENT"]
    score: float = 1.0
    detail: Optional[dict] = None
    ts: float

class AnalyzeResult(BaseModel):
    events: List[Detection] = []
    latency_ms: int = 0

class AnalyzeRequestB64(BaseModel):
    frame_b64: str = Field(..., description="JPEG/PNG base64")

class FaceVerifyRequest(BaseModel):
    selfie_b64: str
    idface_b64: str
    model: str = "ArcFace"  # DeepFace 모델명

class FaceVerifyResult(BaseModel):
    is_match: bool
    distance: float
    threshold: float
    model: str
