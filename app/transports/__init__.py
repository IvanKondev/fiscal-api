"""Transport layer implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTransport(ABC):
    """Abstract byte-pipe shared by serial, TCP, USB and future transports."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def write(self, data: bytes) -> None: ...

    @abstractmethod
    def read(self, size: int = 1) -> bytes: ...
