from __future__ import annotations

import asyncio
import sys
import threading
import time
import webbrowser

import uvicorn

from app.settings import APP_HOST, APP_PORT

# paho-mqtt (used by aiomqtt) requires add_reader/add_writer which
# only work on SelectorEventLoop. Windows defaults to ProactorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_URL = f"http://127.0.0.1:{APP_PORT}"


def _open_browser() -> None:
    """Wait for the server to accept connections, then open the default browser."""
    import socket

    for _ in range(20):
        time.sleep(0.3)
        try:
            with socket.create_connection(("127.0.0.1", APP_PORT), timeout=0.5):
                break
        except OSError:
            continue
    webbrowser.open(_URL)


def main() -> None:
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=False)


if __name__ == "__main__":
    main()
