from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class PrinterAdapter(ABC):
    model: str = ""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def build_payload(self, payload_type: str, payload: Dict[str, Any]) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def build_test_print(self) -> bytes:
        raise NotImplementedError
