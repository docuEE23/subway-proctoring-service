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
