import os
import platform
import subprocess
import threading
import time
import webbrowser

import uvicorn

from app.main import app


HOST = "127.0.0.1"
PORT = 8000

URL = f"http://{HOST}:{PORT}"


def open_browser():
    time.sleep(2)

    system = platform.system()

    try:
        if system == "Windows":
            chrome_paths = [
                os.path.expandvars(
                    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
                ),
                os.path.expandvars(
                    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
                ),
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
                ),
            ]

            for chrome_path in chrome_paths:
                if os.path.exists(
                    chrome_path
                ):
                    subprocess.Popen([
                        chrome_path,
                        URL,
                    ])
                    return

        elif system == "Darwin":
            subprocess.Popen([
                "open",
                "-a",
                "Google Chrome",
                URL,
            ])
            return

    except Exception as error:
        print(
            "Could not open Chrome:",
            error,
        )

    webbrowser.open(URL)


def main():
    print(
        "Starting NexaMind..."
    )

    print(
        f"Open: {URL}"
    )

    threading.Thread(
        target=open_browser,
        daemon=True,
    ).start()

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()