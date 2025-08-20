# ai_server/app/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str

class ImageB64(BaseModel):
    image_b64: str = Field(..., description="base64-encoded image (JPEG/PNG)")

class RTSPRequest(BaseModel):
    rtsp_url: str = Field(..., description="rtsp://user:pass@host:554/...")

class FaceBox(BaseModel):
    x: int; y: int; w: int; h: int; score: float

class DetectResponse(BaseModel):
    count: int; boxes: List[FaceBox]

class VerifyRequest(BaseModel):
    probe_image_b64: str; ref_image_b64: str

class VerifyResponse(BaseModel):
    similarity: float; is_match: bool

class GazeResponse(BaseModel):
    direction: str; confidence: float; box: Optional[FaceBox] = None

# --- 객체 탐지를 위한 신규 스키마 ---
class ObjectBox(BaseModel):
    x: int; y: int; w: int; h: int
    score: float
    label: str = Field(..., description="Detected object name (e.g., cell phone)")

class DetectObjectsResponse(BaseModel):
    count: int
    boxes: List[ObjectBox]
