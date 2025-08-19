import sys
import socketio

path: str = __file__
path = path.replace("\\", "/")
path = "/".join(path.split("/")[:-3])
sys.path.append(path)
sys.path.append(path + "/backend")
sys.path.append(path + "/backend/app")

from fastapi import FastAPI
from db import lifespan
from fastapi.middleware.cors import CORSMiddleware
from api import auth_router, session_router, exam_router
from backend.app.api.websocket import sio

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(session_router, prefix="/api/v1/session", tags=["Sessions"])
app.include_router(exam_router, prefix="/api/v1/exams", tags=["Exams"])

socket_app = socketio.ASGIApp(sio)
app.mount("/ws", socket_app)

@app.get("/")
async def root():
    return {"message": "Online Monitoring System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=7049)