# Subway AI Server

FastAPI 기반의 실시간 프레임 분석/얼굴 대조 서버.

## 실행

### 로컬

```bash
cd ai_server
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```
