from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.db import create_log

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")


def log_info(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    logging.info(message)
    create_log("info", message, context)


def log_warning(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    logging.warning(message)
    create_log("warning", message, context)


def log_error(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    logging.error(message)
    create_log("error", message, context)
