from __future__ import annotations

from typing import Any, Dict

from app.adapters import get_adapter
from app.adapters.datecs_base import DatecsBaseAdapter
from app.app_logging import log_info
from app.datecs_fiscal import fiscal_operation
from app.datecs_print import print_datecs_payload
from app.settings import GLOBAL_DRY_RUN
from app.transports.factory import create_transport


def build_payload(printer: Dict[str, Any], payload_type: str, payload: Dict[str, Any]) -> bytes:
    adapter = get_adapter(printer["model"], printer.get("config") or {})
    if payload_type == "test":
        return adapter.build_test_print()
    return adapter.build_payload(payload_type, payload)


def send_payload(printer: Dict[str, Any], payload_type: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
    adapter = get_adapter(printer["model"], printer.get("config") or {})
    transport_type = (printer.get("transport") or "serial").lower()
    dry_run = GLOBAL_DRY_RUN or bool(printer.get("dry_run"))
    bytes_sent: int | None = None
    mode = "raw"
    fiscal_types = {"fiscal_receipt", "storno", "report", "cash"}
    result = None
    
    if isinstance(adapter, DatecsBaseAdapter):
        # Datecs protocol printers — serial or LAN, same protocol layer
        if payload_type in fiscal_types:
            result = fiscal_operation(printer, adapter, payload_type, payload, dry_run=dry_run)
            mode = "datecs_fiscal"
        else:
            result = print_datecs_payload(printer, adapter, payload_type, payload, dry_run=dry_run)
            mode = "datecs"
    else:
        # Generic raw-data printers
        data = build_payload(printer, payload_type, payload)
        transport = create_transport(printer, dry_run=dry_run)
        transport.write(data)
        transport.close()
        bytes_sent = len(data)

    log_info(
        "PRINT_SENT",
        {"printer_id": printer.get("id"), "bytes": bytes_sent, "mode": mode, "result": result},
    )
    return result
