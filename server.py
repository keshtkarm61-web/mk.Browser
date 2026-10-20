import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI(title="mk.Browser")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>mk.Browser</title>
  <style>
    :root {
      --bg: #070b12;
      --panel: rgba(15, 23, 42, 0.95);
      --line: #334155;
      --text: #edf2ff;
      --muted: #a5b4cf;
      --accent: #60a5fa;
      --accent-2: #8b5cf6;
      --success: #22c55e;
    }

    * { box-sizing: border-box; }

    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0;
      background: linear-gradient(180deg, #020817 0%, #081120 100%);
      color: var(--text);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 18px;
    }

    .app {
      width: min(100%, 760px);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.35);
      padding: 18px;
    }

    .badge {
      display: inline-block;
      background: rgba(34,197,94,0.12);
      border: 1px solid rgba(34,197,94,0.25);
      color: #bbf7d0;
      border-radius: 999px;
      padding: 8px 12px;
      margin-bottom: 12px;
      font-size: 0.8rem;
      font-weight: 700;
    }

    h1 {
      margin: 0 0 8px;
      font-size: clamp(1.7rem, 5vw, 2.4rem);
      font-weight: 800;
      letter-spacing: -0.04em;
    }

    .subtitle {
      margin: 0 0 22px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.7;
    }

    label {
      display: block;
      margin-top: 16px;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 0.9rem;
      font-weight: 700;
    }

    input, textarea, button {
      width: 100%;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(15, 23, 42, 0.9);
      color: var(--text);
      padding: 14px 14px;
      font-size: 1rem;
      outline: none;
    }

    input:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15);
    }

    textarea {
      min-height: 120px;
      resize: vertical;
    }

    button {
      margin-top: 18px;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      border: none;
      font-weight: 800;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }

    button:hover {
      transform: translateY(-1px);
      opacity: 0.96;
    }

    #result {
      margin-top: 18px;
      background: #020817;
      border: 1px solid var(--line);
      border-radius: 12px;
      min-height: 200px;
      padding: 14px;
      white-space: pre-wrap;
      color: #dfeaff;
      overflow: auto;
      line-height: 1.7;
      font-size: 0.9rem;
    }

    .hint {
      margin-top: 10px;
      font-size: 0.8rem;
      color: var(--muted);
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="app">
    <div class="badge">Local only • No login</div>
    <h1>mk.Browser</h1>
    <p class="subtitle">نسخه شخصی و موبایل‌محور. بدون لاگین، اجرا روی کامپیوتر شما، و دسترسی از گوشی از طریق شبکه محلی.</p>

    <label for="url">URL</label>
    <input id="url" value="https://github.com" />

    <label for="goal">وظیفه</label>
    <textarea id="goal">به صفحه برو، اطلاعات مهم را بخوان و نتیجه را خلاصه کن.</textarea>

    <button id="runBtn">اجرا</button>

    <div class="hint">برای گوشی: http://IP_کامپیوتر:8001</div>

    <pre id="result">نتیجه اجرا اینجا نمایش داده می‌شود...</pre>
  </div>

  <script>
    const runBtn = document.getElementById('runBtn');
    const result = document.getElementById('result');

    runBtn.addEventListener('click', async () => {
      const payload = {
        url: document.getElementById('url').value,
        goal: document.getElementById('goal').value
      };

      result.textContent = 'در حال اجرا...';

      try {
        const response = await fetch('/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await response.json();
        result.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        result.textContent = 'خطا: ' + err.message;
      }
    });
  </script>
</body>
</html>
"""

class TaskRequest(BaseModel):
    url: str
    goal: str

playwright = None
browser = None
page = None

async def ensure_browser():
    global playwright, browser, page
    if page is not None:
        return

    playwright = await async_playwright().__aenter__()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page(viewport={"width": 430, "height": 932})

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_PAGE)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/run")
async def run_task(req: TaskRequest):
    global page

    await ensure_browser()

    try:
        await page.goto(req.url, wait_until="domcontentloaded", timeout=60000)
        title = await page.title()
        body_text = await page.locator("body").inner_text()
        summary = re.sub(r"\s+", " ", body_text or "")[:2500]

        return {
            "status": "success",
            "url": req.url,
            "goal": req.goal,
            "title": title,
            "summary": summary,
            "message": "صفحه با موفقیت باز شد."
        }
    except Exception as exc:
        return {
            "status": "error",
            "url": req.url,
            "goal": req.goal,
            "error": str(exc),
            "message": "خطا در اجرای مرورگر رخ داده است."
        }

@app.on_event("shutdown")
async def shutdown_event():
    global page, browser, playwright
    if page:
        await page.close()
    if browser:
        await browser.close()
    if playwright:
        await playwright.__aexit__(None, None, None)
