from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import base64, time, asyncio

from app.schemas import (
    AnalyzeResult, FaceVerifyRequest, FaceVerifyResult,
    AnalyzeRequestB64
)
from app.services.analyzer import Analyzer
from app.models.face_verify import FaceVerifier
from app.config import settings

app = FastAPI(title="Subway AI Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = Analyzer()
face_verifier = FaceVerifier()

@app.get("/health")
def health():
    return {"status": "ok"}

# 1) 단일 프레임 분석 (multipart)
@app.post("/analyze/frame", response_model=AnalyzeResult)
async def analyze_frame(file: UploadFile = File(...)):
    data = await file.read()
    result = analyzer.analyze_bytes(data)
    return result

# 2) 단일 프레임 분석 (base64 JSON)
@app.post("/analyze/frame_b64", response_model=AnalyzeResult)
async def analyze_frame_b64(req: AnalyzeRequestB64):
    img_bytes = base64.b64decode(req.frame_b64)
    result = analyzer.analyze_bytes(img_bytes)
    return result

# 3) WebSocket 스트림 분석 (프레임-by-프레임)
#    클라이언트: 매 메시지에 {"frame_b64": "..."} 전송
@app.websocket("/ws/analyze")
async def ws_analyze(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            frame_b64 = msg.get("frame_b64")
            if not frame_b64:
                await ws.send_json({"error": "frame_b64 required"})
                continue
            img_bytes = base64.b64decode(frame_b64)
            result = analyzer.analyze_bytes(img_bytes)
            await ws.send_json(result.dict())
    except WebSocketDisconnect:
        pass

# 4) 얼굴/신분증 대조
@app.post("/verify/face", response_model=FaceVerifyResult)
async def verify_face(req: FaceVerifyRequest):
    return face_verifier.verify(req)

# 5) 종료 훅(모델 리소스 해제 등 필요시)
@app.on_event("shutdown")
async def on_shutdown():
    analyzer.close()
    face_verifier.close()
