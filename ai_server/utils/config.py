from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
app_name: str = Field("subway-ai-server", env="APP_NAME")
env: str = Field("dev", env="APP_ENV")
log_level: str = Field("INFO", env="LOG_LEVEL")
preload_models: bool = Field(True, env="PRELOAD_MODELS")


# Face verification
face_verify_threshold: float = Field(0.35, env="FACE_VERIFY_THRESHOLD") # ArcFace cosine(원래는 0.3~0.5 권장)
face_embedder_path: str = Field("app/models/assets/mobilefacenet_arcface.onnx", env="FACE_EMBEDDER_PATH")


class Config:
env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
return Settings()
