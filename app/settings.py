from __future__ import annotations

import os
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = Path(os.getenv("PRINT_GATEWAY_DB", str(DATA_DIR / "print_gateway.sqlite")))

APP_HOST = os.getenv("PRINT_GATEWAY_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("PRINT_GATEWAY_PORT", "8787"))

JOB_POLL_INTERVAL = float(os.getenv("PRINT_GATEWAY_POLL_INTERVAL", "1.0"))
JOB_TIMEOUT_SECONDS = float(os.getenv("PRINT_GATEWAY_JOB_TIMEOUT", "15"))
JOB_MAX_RETRIES = int(os.getenv("PRINT_GATEWAY_JOB_RETRIES", "1"))

DATECS_BAUDRATES = [
    int(value)
    for value in os.getenv("PRINT_GATEWAY_DATECS_BAUDRATES", "9600,19200,38400,57600,115200").split(",")
    if value.strip()
]
DATECS_DETECT_TIMEOUT_MS = int(os.getenv("PRINT_GATEWAY_DETECT_TIMEOUT_MS", "600"))

GLOBAL_DRY_RUN = _env_bool("PRINT_GATEWAY_DRY_RUN", False)

STATIC_DIR = ROOT_DIR / "app" / "static"
