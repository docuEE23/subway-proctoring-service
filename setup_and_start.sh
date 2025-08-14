#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------
# Subway Proctoring Service - 1-click dev start
# - Creates one Python venv at repo root
# - Installs combined requirements (backend + AI)
# - Installs frontend deps
# - Writes .env samples if missing
# - Starts Backend, AI server, Frontend together
# ----------------------------------------------

REPO_ROOT="$(pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo ">> Checking prerequisites..."
command -v node >/dev/null 2>&1 || { echo "!! Node.js가 필요합니다 (>=20)"; exit 1; }
command -v npm  >/dev/null 2>&1 || { echo "!! npm이 필요합니다"; exit 1; }
command -v "${PYTHON_BIN}" >/dev/null 2>&1 || { echo "!! Python이 필요합니다 (>=3.10)"; exit 1; }

echo ">> Creating Python venv at ${VENV_DIR} (if not exists)..."
if [ ! -d "${VENV_DIR}" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip

if [ ! -f "${REPO_ROOT}/requirements.txt" ]; then
  echo "!! requirements.txt가 없습니다. 스크립트와 함께 제공된 requirements.txt를 루트에 배치하세요."
  exit 1
fi

echo ">> Installing Python requirements (root/requirements.txt)..."
pip install -r "${REPO_ROOT}/requirements.txt"

# Ensure folder existence
mkdir -p "${REPO_ROOT}/backend/app" "${REPO_ROOT}/ai_server" "${REPO_ROOT}/frontend"

# Write .env samples if missing
if [ ! -f "${REPO_ROOT}/backend/app/.env" ]; then
  cat > "${REPO_ROOT}/backend/app/.env" <<'EOF'
PORT=8000
ENV=dev
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
# REDIS_URL=redis://localhost:6379/0
EOF
  echo ">> Wrote backend/app/.env"
fi

if [ ! -f "${REPO_ROOT}/ai_server/.env" ]; then
  cat > "${REPO_ROOT}/ai_server/.env" <<'EOF'
AI_SERVER_PORT=8100
AI_MODEL_PATH=./models
EOF
  echo ">> Wrote ai_server/.env"
fi

if [ ! -f "${REPO_ROOT}/frontend/.env" ]; then
  cat > "${REPO_ROOT}/frontend/.env" <<'EOF'
VITE_API_BASE=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
EOF
  echo ">> Wrote frontend/.env"
fi

# Frontend deps
echo ">> Installing frontend dependencies..."
pushd "${REPO_ROOT}/frontend" >/dev/null
if [ -f package-lock.json ] || [ -f package.json ]; then
  npm install
else
  echo "!! frontend/package.json 이 없습니다. 프런트엔드 템플릿을 먼저 추가하세요."
fi
popd >/dev/null

# ---- Start services in background with logs ----
LOG_DIR="${REPO_ROOT}/.logs"
mkdir -p "${LOG_DIR}"

# Backend start (try common entrypoints)
start_backend() {
  echo ">> Starting Backend (FastAPI/uvicorn) on :8000"
  cd "${REPO_ROOT}/backend/app" || exit 1
  (
    set +e
    # 1) app.main:app  2) main:app  3) backend.app.main:app
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload       || uvicorn main:app --host 0.0.0.0 --port 8000 --reload       || uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
  ) >> "${LOG_DIR}/backend.log" 2>&1 &
  echo $! > "${LOG_DIR}/backend.pid"
}

# AI server start (try common entrypoints)
start_ai() {
  echo ">> Starting AI Server on :8100"
  cd "${REPO_ROOT}/ai_server" || exit 1
  (
    set +e
    uvicorn ai_main:app --host 0.0.0.0 --port 8100 --reload       || uvicorn main:app --host 0.0.0.0 --port 8100 --reload
  ) >> "${LOG_DIR}/ai.log" 2>&1 &
  echo $! > "${LOG_DIR}/ai.pid"
}

start_frontend() {
  echo ">> Starting Frontend (npm run dev)"
  cd "${REPO_ROOT}/frontend" || exit 1
  ( npm run dev ) >> "${LOG_DIR}/frontend.log" 2>&1 &
  echo $! > "${LOG_DIR}/frontend.pid"
}

start_backend || true
start_ai || true
start_frontend || true

echo "----------------------------------------------"
echo "All services attempted to start."
echo " - Backend : http://localhost:8000 (logs: .logs/backend.log)"
echo " - AI      : http://localhost:8100 (logs: .logs/ai.log)"
echo " - Frontend: http://localhost:5173 or 3000 (logs: .logs/frontend.log)"
echo "----------------------------------------------"
echo "Stop with: kill $(cat .logs/backend.pid .logs/ai.pid .logs/frontend.pid 2>/dev/null | xargs) || true"
