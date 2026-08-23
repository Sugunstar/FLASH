import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("URL")
CLASS_TOKEN = os.getenv("CLASS_TOKEN", "changeme")


def send_text(text):
    try:
        headers = {"X-Class-Token": CLASS_TOKEN}
        response = requests.post(SERVER_URL, json={"text": text}, headers=headers, timeout=5) # type: ignore
        response.raise_for_status()
        if text.strip() == "CLEAR":
            print("[Cleared]")
        else:
            print("[Sent]")
    except requests.RequestException as exc:
        print(f"[Connection error] {exc}")


def main():
    buffer = []
    print("Live code client started. Type lines and end with SEND, or type CLEAR.")

    try:
        while True:
            line = input()
            if line.strip() == "CLEAR":
                send_text("CLEAR")
                buffer.clear()
            elif line.strip() == "SEND":
                if buffer:
                    payload = "\n".join(buffer)
                    send_text(payload)
                    buffer.clear()
                else:
                    print("[Nothing to send]")
            else:
                buffer.append(line)
    except KeyboardInterrupt:
        print("\nExiting cleanly.")
    except EOFError:
        print("\nExiting cleanly.")


if __name__ == "__main__":
    main()