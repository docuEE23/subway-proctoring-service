# subway-proctoring AI (Lite + Accurate)


## Quickstart
```bash
cd ai_server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
