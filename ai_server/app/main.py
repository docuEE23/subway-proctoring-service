# ai_server/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .schemas import (
    ImageB64, RTSPRequest, DetectResponse, ErrorResponse,
    VerifyRequest, VerifyResponse, GazeResponse, FaceBox,
    DetectObjectsResponse # 신규 import
)
from .services.analyzer import Analyzer
from .utils.config import get_settings

analyzer = Analyzer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if get_settings().preload_models:
        analyzer.preload()
    yield

app = FastAPI(title="subway-proctoring ai (lite+accurate)", lifespan=lifespan)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/v1/detect", response_model=DetectResponse, responses={400: {"model": ErrorResponse}})
async def detect(req: ImageB64):
    try:
        out = analyzer.detect(req.image_b64)
        boxes = [FaceBox(**b) for b in out["boxes"]]
        return {"count": len(boxes), "boxes": boxes}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/verify", response_model=VerifyResponse, responses={400: {"model": ErrorResponse}})
async def verify(req: VerifyRequest):
    try:
        return analyzer.verify(req.probe_image_b64, req.ref_image_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/gaze", response_model=GazeResponse, responses={400: {"model": ErrorResponse}})
async def gaze(req: ImageB64):
    try:
        out = analyzer.gaze(req.image_b64)
        if out.get("box") is not None:
            out["box"] = FaceBox(**out["box"])
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 신규 객체 탐지 API 엔드포인트 ---
@app.post("/v1/detect_objects", response_model=DetectObjectsResponse, responses={400: {"model": ErrorResponse}})
async def detect_objects(req: ImageB64):
    try:
        out = analyzer.detect_objects(req.image_b64)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/rtsp/detect", response_model=DetectResponse, responses={400: {"model": ErrorResponse}})
async def detect_rtsp(req: RTSPRequest):
    try:
        out = analyzer.detect_rtsp(req.rtsp_url)
        boxes = [FaceBox(**b) for b in out["boxes"]]
        return {"count": len(boxes), "boxes": boxes}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/rtsp/gaze", response_model=GazeResponse, responses={400: {"model": ErrorResponse}})
async def gaze_rtsp(req: RTSPRequest):
    try:
        out = analyzer.gaze_rtsp(req.rtsp_url)
        if out.get("box") is not None:
            out["box"] = FaceBox(**out["box"])
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 신규 RTSP 객체 탐지 API 엔드포인트 ---
@app.post("/v1/rtsp/detect_objects", response_model=DetectObjectsResponse, responses={400: {"model": ErrorResponse}})
async def detect_objects_rtsp(req: RTSPRequest):
    try:
        out = analyzer.detect_objects_rtsp(req.rtsp_url)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
