# mk.Browser

A local browser automation prototype for mobile-first use. It runs on your machine and can be accessed from a phone over the local network without login.

## Features
- Local-only browser automation
- Mobile-friendly HTML UI
- Playwright browser control
- FastAPI backend
- No login required

## Setup

### 1) Install dependencies
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2) Run the app
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

### 3) Open from phone
Find your computer IP and open:
```text
http://IP_کامپیوتر:8001
```
For example:
```text
http://192.168.1.20:8001
```

## Notes
This is a local prototype for experimentation. It is designed for use on the same LAN as your computer and does not require user authentication.
