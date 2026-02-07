"""Abstract base for protocol-specific data builders.

Each Datecs printer series (FP-700MX, FP-2000, …) has its own wire format
for the *same* command codes.  A concrete ``DatecsDataBuilder`` knows how to
serialise command parameters into the format that its series expects.

Adding a new series = subclass this and implement every method.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class DatecsDataBuilder(ABC):
    """One method per command whose DATA area differs across series."""

    # ------------------------------------------------------------------
    # 0x30  Open fiscal receipt
    # ------------------------------------------------------------------
    @abstractmethod
    def open_receipt(
        self,
        op_num: str,
        password: str,
        till: str,
        invoice: str = "",
        nsale: str = "",
    ) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x31  Register sale
    # ------------------------------------------------------------------
    @abstractmethod
    def sale(self, item: Dict[str, Any]) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x35  Payment / total
    # ------------------------------------------------------------------
    @abstractmethod
    def payment(self, payment: Dict[str, Any]) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x2A  Free text in a service (non-fiscal) receipt
    # ------------------------------------------------------------------
    @abstractmethod
    def nonfiscal_text(self, text: str) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x36  Free text in a fiscal receipt
    # ------------------------------------------------------------------
    @abstractmethod
    def fiscal_text(self, text: str) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x46  Service deposit / withdrawal
    # ------------------------------------------------------------------
    @abstractmethod
    def cash(self, payload: Dict[str, Any]) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x45  Daily financial report (Z / X)
    # ------------------------------------------------------------------
    @abstractmethod
    def report(self, payload: Dict[str, Any]) -> str:
        ...

    # ------------------------------------------------------------------
    # 0x4A  Status request data byte
    # ------------------------------------------------------------------
    @abstractmethod
    def status_data(self) -> str:
        ...

    # ------------------------------------------------------------------
    # Helpers shared by all series
    # ------------------------------------------------------------------
    @staticmethod
    def format_amount(value: Any, precision: int = 2) -> str:
        if value is None or value == "":
            return ""
        try:
            return f"{float(value):.{precision}f}"
        except (ValueError, TypeError):
            return str(value)
