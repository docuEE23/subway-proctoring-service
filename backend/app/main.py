from fastapi import FastAPI
from db import lifespan
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import auth_router

app = FastAPI(lifespan=lifespan)
# app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
# app.include_router(signal_router)

@app.get("/")
async def root():
    return {"message": "Online Monitoring System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=7049)