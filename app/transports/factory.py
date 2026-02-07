"""Factory that builds the correct transport from a printer dict."""
from __future__ import annotations

from typing import Any, Dict

from app.transports import BaseTransport


def create_transport(printer: Dict[str, Any], dry_run: bool = False) -> BaseTransport:
    """Return the appropriate transport for a printer configuration.

    Supports: serial, lan (tcp).  Easily extensible for future types.
    """
    transport_type = (printer.get("transport") or "serial").lower()

    if transport_type == "serial":
        from app.transports.serial_transport import SerialConfig, SerialTransport

        port = printer.get("port")
        if not port:
            raise ValueError("Serial transport requires a COM port.")
        config = SerialConfig(
            port=port,
            baudrate=int(printer.get("baudrate", 9600)),
            data_bits=int(printer.get("data_bits", 8)),
            parity=str(printer.get("parity", "N")),
            stop_bits=float(printer.get("stop_bits", 1)),
            timeout_ms=int(printer.get("timeout_ms", 5000)),
        )
        return SerialTransport(config, dry_run=dry_run)

    if transport_type == "lan":
        from app.transports.tcp_transport import TcpConfig, TcpTransport

        ip_address = printer.get("ip_address")
        if not ip_address:
            raise ValueError("LAN transport requires an IP address.")
        config = TcpConfig(
            ip_address=ip_address,
            tcp_port=int(printer.get("tcp_port", 4999)),
            timeout_ms=int(printer.get("timeout_ms", 5000)),
        )
        return TcpTransport(config, dry_run=dry_run)

    raise ValueError(f"Unsupported transport type: {transport_type}")
