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
    <title>Live Code Board</title>
    <style>
      body {
        margin: 0;
        background: #0f172a;
        color: #e2e8f0;
        font-family: "Consolas", "Monaco", monospace;
        height: 100vh;
        overflow: hidden;
      }
      pre {
        margin: 0;
        padding: 24px;
        height: 100vh;
        box-sizing: border-box;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 22px;
        line-height: 1.45;
      }
    </style>
  </head>
  <body>
    <pre id="board">Loading...</pre>
    <script>
      async function refreshBoard() {
        try {
          const response = await fetch('/content');
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          const data = await response.json();
          document.getElementById('board').textContent = data.content || '';
        } catch (error) {
          console.error('Failed to fetch board content:', error);
        }
      }
      refreshBoard();
      setInterval(refreshBoard, 1000);
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