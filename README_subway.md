
# Subway Proctoring Service

AI를 활용한 **비대면 자격검정 통합 감독 서비스** 모놀리포지토리입니다.  
이 저장소는 크게 **frontend**, **backend**, **ai_server**로 구성되어 있으며, 설계서 기반의 원격시험 서비스(응시자·감독관·관리자)를 로컬에서 실행할 수 있도록 기본 실행 방법과 의존성을 정리했습니다.

> 레포지토리: https://github.com/docuEE23/subway-proctoring-service

---

## 아키텍처 개요

- **frontend/**: 웹 클라이언트(React/Vite 기준 가정). API 서버와 WebSocket에 연결하여 응시/감독 UI 제공
- **backend/app/**: API 서버(FastAPI/uvicorn 기준 가정). 인증, 세션/응시자/감독 제어 API, WebSocket 이벤트
- **ai_server/**: 부정행위 감지 등 AI 서브서비스(Python 기반 가정). 웹캠/스크린 이벤트 신호 처리

> 폴더 구조는 레포지토리의 디렉터리명을 기준으로 작성되었습니다(변경 시 아래 명령의 경로만 맞춰 주세요).

---

## 사전 준비물 (Prerequisites)

- **Node.js** 20.x 이상 (LTS 권장)
- **Python** 3.10 ~ 3.12 (3.11 권장), `pip` 또는 `uv` 사용 가능
- (선택) **Redis** 6+ — 세션/큐(선택), **FFmpeg** — 미디어 처리(선택)

---

## 빠른 시작(Quickstart)

### 1) 저장소 클론
```bash
git clone https://github.com/docuEE23/subway-proctoring-service.git
cd subway-proctoring-service
```

### 2) Frontend 설치 및 실행
```bash
cd frontend
# 패키지 설치 (npm 또는 pnpm 사용)
npm install
# 개발 서버 실행 (기본: http://localhost:5173 또는 3000)
npm run dev
```
> API 서버 경로를 환경변수로 쓰는 경우: `.env` 또는 `.env.local`에 `VITE_API_BASE=http://localhost:8000` 설정

### 3) Backend 설치 및 실행 (FastAPI 가정)
```bash
cd ../backend/app
# 가상환경 생성 & 활성화 (예: venv)
python -m venv .venv
# Windows: .venv\Scripts\activate, macOS/Linux: source .venv/bin/activate
pip install --upgrade pip

# 필요 패키지 설치 (requirements.txt가 있다면)
pip install -r requirements.txt
# 없다면 대표 패키지 예시:
# pip install fastapi uvicorn[standard] pydantic[dotenv] python-multipart websockets

# 개발 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
> **모듈명(main, app 등)**은 실제 코드 기준으로 조정하세요. (예: `uvicorn app.main:app`)

### 4) AI Server 설치 및 실행 (선택)
```bash
cd ../../ai_server
python -m venv .venv
# Windows: .venv\Scripts\activate, macOS/Linux: source .venv/bin/activate
pip install --upgrade pip

# 필요 패키지 설치 (requirements.txt가 있다면)
pip install -r requirements.txt
# 없다면 예시(가정): 
# pip install opencv-python numpy mediapipe fastapi uvicorn

# 예시 실행 (모듈명/엔트리 조정 필요)
# uvicorn ai_main:app --host 0.0.0.0 --port 8100 --reload
```

---

## 환경 변수 샘플(.env)

### Backend (`backend/app/.env` 예시)

```
# 서버
PORT=8000
ENV=dev
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT/세션
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60

# (선택) Redis
REDIS_URL=redis://localhost:6379/0
```

### Frontend (`frontend/.env` 또는 `.env.local` 예시)

```
VITE_API_BASE=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### AI Server (`ai_server/.env` 예시)

```
AI_SERVER_PORT=8100
AI_MODEL_PATH=./models
```

---

## 일반적인 실행 순서

1. **Backend** 기동 → `http://localhost:8000/docs` (OpenAPI 문서가 있다면 확인)
2. **AI Server** 기동(선택) → `http://localhost:8100`
3. **Frontend** 기동 → 브라우저에서 `http://localhost:5173` 접속  
   - 로그인 → 역할별 화면 진입(응시자/감독관/관리자)
   - API/WS 경로가 다르면 `.env`로 조정

---

## 스크립트/패키지 힌트(변경 가능)

- Frontend: `npm run dev`, `npm run build`, `npm run preview`
- Backend: `uvicorn <module>:app --reload` / `python -m uvicorn <module>:app --reload`
- AI Server: `uvicorn <module>:app --reload`

> 위 명령은 **가이드용**이며, 실제 파일명/엔트리포인트에 맞게 조정하세요.

---

## 문제 해결(Troubleshooting)

- **CORS 오류**: Backend의 `CORS_ORIGINS`에 Frontend 주소를 추가
- **포트 충돌**: Frontend(5173/3000), Backend(8000), AI(8100) 포트를 변경
- **의존성 미정**: `requirements.txt`/`package.json` 확인 후 누락 패키지 설치

---

## 라이선스

레포지토리의 `LICENSE` 파일을 확인하세요(없다면 사내/프로젝트 정책에 따릅니다).
