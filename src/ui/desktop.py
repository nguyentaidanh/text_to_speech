import sys
import os
from pathlib import Path

# Automatically add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import webbrowser
import uvicorn
import threading
import time

def start_server():
    from src.api.server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def main():
    print("Starting VietTTS Studio Server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)

    print("Opening VietTTS Studio Application UI at http://127.0.0.1:8000/studio ...")
    webbrowser.open("http://127.0.0.1:8000/studio")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping VietTTS Studio...")

if __name__ == "__main__":
    main()
