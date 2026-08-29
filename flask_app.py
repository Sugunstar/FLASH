from flask import Flask, jsonify, render_template_string, request
import os

app = Flask(__name__)

board = {"content": ""}
CLASS_TOKEN = os.getenv("CLASS_TOKEN", "changeme")

HTML_PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Live Code Board – FLASH</title>

    <!-- Highlight.js: syntax highlighting with auto-detection -->
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/stackoverflow-light.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

    <style>
      *, *::before, *::after { box-sizing: border-box; }

      body {
        margin: 0;
        background: #fef08a;   /* warm yellow */
        color: #1a1a1a;        /* near-black text */
        font-family: "Consolas", "Monaco", monospace;
        height: 100vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
      }

      /* ── Top bar ── */
      #topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 24px;
        background: #ca8a04;   /* deep amber */
        border-bottom: 2px solid #a16207;
        flex-shrink: 0;
      }
      #topbar .logo {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #1a1a1a;
        text-transform: uppercase;
      }
      #lang-badge {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: #fef08a;
        color: #713f12;
        border: 1px solid #a16207;
        border-radius: 6px;
        padding: 3px 10px;
      }

      /* ── Code area ── */
      #code-wrap {
        flex: 1;
        overflow: auto;
        padding: 0;
      }

      pre#board {
        margin: 0;
        padding: 24px;
        min-height: 100%;
        background: transparent !important;
        font-size: 20px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        color: #1a1a1a;
      }

      /* Keep hljs background transparent so yellow bg shows through */
      .hljs {
        background: transparent !important;
        color: #1a1a1a;
      }

      /* Subtle fade-in when content updates */
      @keyframes flash-in {
        from { opacity: 0.4; }
        to   { opacity: 1; }
      }
      .updated {
        animation: flash-in 0.35s ease;
      }
    </style>
  </head>
  <body>
    <div id="topbar">
      <span class="logo">⚡ FLASH</span>
      <span id="lang-badge">waiting…</span>
    </div>

    <div id="code-wrap">
      <pre id="board"><code id="code">Loading…</code></pre>
    </div>

    <script>
      const codeEl = document.getElementById('code');
      const badge  = document.getElementById('lang-badge');
      let loadedContent = null;

      // 1. Fetch current content from server, use it as the baseline,
      //    and apply syntax highlighting immediately.
      async function init() {
        try {
          const res  = await fetch('/content');
          const data = await res.json();
          const content = (data.content || '').trim();
          loadedContent = content;

          if (content) {
            const result = hljs.highlightAuto(content);
            codeEl.innerHTML = result.value;
            badge.textContent = result.language || 'plain text';
          } else {
            codeEl.textContent = '';
            badge.textContent = 'waiting…';
          }
        } catch (e) {
          badge.textContent = 'error';
        }
      }

      // 2. Poll every second — reload ONLY if server content changed.
      async function pollForChanges() {
        try {
          const res    = await fetch('/content');
          const data   = await res.json();
          const latest = (data.content || '').trim();

          if (loadedContent !== null && latest !== loadedContent) {
            window.location.reload();
          }
        } catch (e) {
          // network blip — ignore and retry next tick
        }
      }

      init().then(() => setInterval(pollForChanges, 1000));
    </script>
  </body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(HTML_PAGE)


@app.get("/content")
def get_content():
    return jsonify({"content": board["content"]})


@app.post("/update")
def update_content():
    if request.headers.get("X-Class-Token") != CLASS_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "text must be a string"}), 400

    if text.strip() == "CLEAR":
        board["content"] = ""
        return jsonify({"status": "cleared"})

    if board["content"]:
        board["content"] = board["content"] + "\n\n" + text
    else:
        board["content"] = text

    return jsonify({"status": "updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)