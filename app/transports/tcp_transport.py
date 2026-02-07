from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Optional

from app.app_logging import log_info, log_warning
from app.transports import BaseTransport


@dataclass
class TcpConfig:
    ip_address: str
    tcp_port: int = 4999
    timeout_ms: int = 5000


class TcpTransport(BaseTransport):
    """TCP socket transport for Datecs printers connected via LAN."""

    def __init__(self, config: TcpConfig, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run
        self._sock: Optional[socket.socket] = None

    def open(self) -> None:
        if self.dry_run:
            return
        if self._sock is not None:
            return
        timeout_s = self.config.timeout_ms / 1000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_s)
        try:
            sock.connect((self.config.ip_address, self.config.tcp_port))
        except OSError as exc:
            sock.close()
            raise RuntimeError(
                f"Cannot connect to printer at {self.config.ip_address}:{self.config.tcp_port} — {exc}"
            ) from exc
        self._sock = sock

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def write(self, data: bytes) -> None:
        if self.dry_run:
            log_info("DRY_RUN_TCP_WRITE", {"bytes_hex": data.hex(), "length": len(data)})
            return
        self.open()
        if not self._sock:
            raise RuntimeError("TCP connection not initialized")
        self._sock.sendall(data)

    def read(self, size: int = 1) -> bytes:
        if self.dry_run:
            return b""
        self.open()
        if not self._sock:
            raise RuntimeError("TCP connection not initialized")
        try:
            data = self._sock.recv(size)
            return data
        except socket.timeout:
            return b""
        except OSError:
            return b""
