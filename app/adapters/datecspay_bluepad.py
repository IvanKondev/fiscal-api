"""DatecsPay BluePad card reader (pinpad) adapter.

This is a non-fiscal device — it handles card payments only.
Fiscal operations (receipts, storno, reports) are NOT supported.
Use pinpad_* payload types for card operations.
"""
from __future__ import annotations

from typing import Any, Dict

from app.adapters.base import PrinterAdapter


class DatecsPayBluePadAdapter(PrinterAdapter):
    model = "datecspay_bluepad"

    def build_payload(self, payload_type: str, payload: Dict[str, Any]) -> bytes:
        raise NotImplementedError(
            "BluePad is a card reader, not a fiscal printer. "
            "Use pinpad_* payload types (pinpad_purchase, pinpad_void, etc.)."
        )

    def build_test_print(self) -> bytes:
        raise NotImplementedError(
            "BluePad does not support printing. Use pinpad_ping to test connectivity."
        )
