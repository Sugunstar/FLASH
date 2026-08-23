# FLASH – Fast Live Automated Sharing Hub

**FLASH** is a minimal, real‑time code‑clipboard designed for live teaching scenarios.  
A teacher types code in a terminal (or any HTTP client) and hits **SEND**; the snippet is instantly posted to a shared board that every student sees in their browser. The board updates every second via a lightweight polling loop, giving a near‑zero‑latency experience.

---

## Why FLASH?

- **Instant sharing** – No manual copy‑paste; code appears on all student screens as soon as the teacher sends it.
- **Zero‑setup for students** – They only need a web browser (or the tiny Python client) and the board URL.
- **Simple clear/reset** – A single `CLEAR` command wipes the board for the next topic.
- **Lightweight & dependency‑free** – Built with Flask and a few standard libraries; runs anywhere Python is available.
- **Secure writes** – Optional token‑based protection (`CLASS_TOKEN`) prevents unauthorized writes while keeping reads open.
- **Ideal for live coding, algorithm walk‑throughs, debugging demos, and quick exercises** where every line matters.

---

## Project Structure

```
flask_app/
├─ flask_app.py      # Flask server (serves HTML, provides /content & /update endpoints)
├─ client.py         # Terminal client for the teacher (or any HTTP POST tool)
├─ requirements.txt  # File to download all required packages
├─ .env              # Configuration: URL and CLASS_TOKEN
└─ README.md         # This file

```

---

## Getting Started (Local Development)

### Prerequisites
- Python 3.8+
- `pip` (Python package manager)

### Installation
```bash
# Clone or copy the project folder
cd path/to/flask_app

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt   # If you have a requirements.txt, otherwise:
pip install flask requests python-dotenv
```

> **Note:** If you don’t have a `requirements.txt`, you can create one with:
> ```
> flask>=3.0
> requests>=2.0
> python-dotenv>=1.0
> ```

### Configuration
Create (or edit) `.env` in the project root:
```dotenv
# URL where the Flask app will be reachable (for the client)
URL="http://127.0.0.1:5000/update"

# Optional token to protect write endpoints.
# If omitted, the default "changeme" is used.
CLASS_TOKEN=your-secret-token-here
```

### Run the Server
```bash
python flask_app.py
```
- The server starts on `http://0.0.0.0:5000`.
- Open a browser to `http://127.0.0.1:5000/` to view the live board.

### Run the Teacher Client
In a separate terminal:
```bash
python client.py
```
- Type or paste lines of code.
- When ready, type **SEND** to post the buffered lines to the board.
- Type **CLEAR** then **SEND** to erase the board.
- Type `Ctrl+C` or `Ctrl+D` to exit cleanly.

Students only need to open the board URL (`http://<server-host>:5000/`) in any browser; they will see updates automatically.

---

## Deploying to PythonAnywhere (Recommended)

PythonAnywhere provides a free tier that is perfect for hosting FLASH for a classroom.

### Step‑by‑Step

1. **Create an account** at <https://www.pythonanywhere.com/> and log in.
2. **Go to the *Web* tab** → **Add a new web app**.
3. Choose **Manual configuration** → **Python 3.9** (or the latest available).
4. Set the **Application URL** (e.g., `yourusername.pythonanywhere.com`).
5. **Configure the virtualenv** (optional):
   - In the *Web* tab, under *Virtualenv*, create a new virtualenv (e.g., `flash-env`).
   - Activate it via the *Consoles* tab if you need to install packages manually.
6. **Upload the project files**:
   - Use the *Files* tab to upload `flask_app.py`, `client.py`, and create a `.env` file.
   - Alternatively, clone a Git repository if you prefer.
7. **Install dependencies** via a console:
   ```bash
   # In a Bash console (from the *Consoles* tab)
   workon flash-env   # if you created a virtualenv
   pip install flask requests python-dotenv
   ```
8. **Edit the WSGI configuration file** (the one PythonAnywhere auto‑generated, e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import os
   import sys

   # Add your project directory to the path
   project_home = '/home/yourusername/flash_app'   # <-- adjust to your actual path
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   from flask_app import app as application  # <-- expose the Flask app

   # Load environment variables from .env
   from dotenv import load_dotenv
   load_dotenv(os.path.join(project_home, '.env'))
   ```
9. **Set the web app to reload** (click the *Reload* button on the *Web* tab).
10. **Visit your board**: `https://yourusername.pythonanywhere.com/`
    - The teacher runs `client.py` locally (or on any machine) with `URL` pointing to `https://yourusername.pythonanywhere.com/update`.
    - Students view the board at `https://yourusername.pythonanywhere.com/`.

### Environment Variables on PythonAnywhere
- In the *Web* tab → *Environment variables* section, add:
  - `URL` – the full update URL (the same as above)
  - `CLASS_TOKEN` – your secret token for write protection
- Alternatively, keep them in the `.env` file; the WSGI script above loads it.

---

## How the Class Token Works

- **Purpose:** Protects the `/update` endpoint so only authorized parties (the teacher or trusted clients) can modify the board.
- **Implementation:**
  ```python
  CLASS_TOKEN = os.getenv("CLASS_TOKEN", "changeme")
  ...
  @app.post("/update")
  def update_content():
      if request.headers.get("X-Class-Token") != CLASS_TOKEN:
          return jsonify({"error": "unauthorized"}), 401
      # … normal processing …
  ```
- **Usage:**
  - Set `CLASS_TOKEN` in `.env` (or as an environment variable) to any string you like.
  - The teacher’s client automatically adds the header `X-Class-Token: <token>` to every POST.
  - If the header is missing or incorrect, the server responds with **401 Unauthorized** and does not modify the board.
- **Read endpoints (`/` and `/content`) remain open**; no token is required to view the board.
- **Tip:** For extra safety, regenerate the token periodically and update both server and client.

---

## Advanced Tweaks (Optional) (for devs who want to contribute)

| Feature | How to Add |
|---------|------------|
| **Replace mode** (overwrite instead of append) | Add a query parameter `?mode=replace` to `/update` and adjust logic accordingly. |
| **Maximum board size** | After appending, trim: `if len(board["content"]) > MAX_CHARS: board["content"] = board["content"][-MAX_CHARS:]` |
| **Persistence across restarts** | Save `board["content"]` to a file (e.g., `/tmp/board.txt`) on each update and load it at startup. |
| **Syntax highlighting** | Include a client‑side library like Prism.js or highlight.js in the HTML and apply it to the `<pre>` after each update. |
| **Timestamps / author info** | Prefix each POST with a timestamp and optional name before appending to the board. |
| **Dockerize** | Write a `Dockerfile` that copies the code, installs dependencies, and runs `flask_app.py`. |
| **Multiple boards / rooms** | Add a room identifier in the URL (e.g., `/room/<id>`) and maintain a dictionary of boards. |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `401 Unauthorized` when sending code | Wrong or missing `CLASS_TOKEN` | Verify `.env` contains the same token on server and client; ensure client sends `X-Class-Token` header. |
| Board not updating in browser | Server not reachable or JavaScript blocked | Check that the server is running and accessible; open browser console for errors. |
| Client shows `[Connection error]` | Incorrect `URL` or network issue | Confirm `URL` points to the correct `/update` endpoint; test with `curl` or Postman. |
| Board grows huge and slow | No size limit | Implement a maximum character limit or periodic clearing. |
| No output in terminal client | Input buffering issues | Ensure you type `SEND` on its own line; the client only sends on that command. |

---

## License

This project is released under the **MIT License** – feel free to copy, modify, and distribute it for educational or any other purpose.

---

## Happy Teaching!

With FLASH you can focus on the code and the conversation, not on the mechanics of sharing it. Set it up once, protect it with a simple token, and let the live board do the rest.

*If you have ideas for further improvements or run into any issues, please open an issue or drop a note – we’re glad to help!*  

--- 

*Created with ❤️ for educators who love live demos.*
