from __future__ import annotations

import uvicorn

from app.settings import APP_HOST, APP_PORT


def main() -> None:
    uvicorn.run("app.main:app", host=APP_HOST, port=APP_PORT, reload=False)


if __name__ == "__main__":
    main()
