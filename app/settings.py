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

# ── MQTT ──────────────────────────────────────────────────────────
MQTT_ENABLED = _env_bool("MQTT_ENABLED", False)
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "fiscal-api")
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "fiscal")
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
MQTT_USE_TLS = _env_bool("MQTT_USE_TLS", False)
