from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import serial
from serial.tools import list_ports

from app.app_logging import log_info, log_warning
from app.transports import BaseTransport


@dataclass
class SerialConfig:
    port: str
    baudrate: int = 9600
    data_bits: int = 8
    parity: str = "N"
    stop_bits: float = 1
    timeout_ms: int = 5000


class SerialTransport(BaseTransport):
    def __init__(self, config: SerialConfig, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run
        self._serial: Optional[serial.Serial] = None

    def open(self) -> None:
        if self.dry_run:
            return
        if self._serial and self._serial.is_open:
            return
        self._serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self._bytesize(self.config.data_bits),
            parity=self._parity(self.config.parity),
            stopbits=self._stopbits(self.config.stop_bits),
            timeout=self.config.timeout_ms / 1000,
            write_timeout=self.config.timeout_ms / 1000,
        )

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()

    def write(self, data: bytes) -> None:
        if self.dry_run:
            log_info("DRY_RUN_SERIAL_WRITE", {"bytes_hex": data.hex(), "length": len(data)})
            return
        self.open()
        if not self._serial:
            raise RuntimeError("Serial connection not initialized")
        self._serial.write(data)
        self._serial.flush()

    def read(self, size: int = 1) -> bytes:
        if self.dry_run:
            return b""
        self.open()
        if not self._serial:
            raise RuntimeError("Serial connection not initialized")
        return self._serial.read(size)

    @staticmethod
    def _bytesize(data_bits: int) -> int:
        mapping = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }
        return mapping.get(data_bits, serial.EIGHTBITS)

    @staticmethod
    def _parity(value: str) -> str:
        value = value.upper()
        mapping = {
            "N": serial.PARITY_NONE,
            "E": serial.PARITY_EVEN,
            "O": serial.PARITY_ODD,
            "M": serial.PARITY_MARK,
            "S": serial.PARITY_SPACE,
        }
        return mapping.get(value, serial.PARITY_NONE)

    @staticmethod
    def _stopbits(value: float) -> float:
        mapping = {1: serial.STOPBITS_ONE, 1.5: serial.STOPBITS_ONE_POINT_FIVE, 2: serial.STOPBITS_TWO}
        return mapping.get(value, serial.STOPBITS_ONE)


def list_serial_ports() -> list[dict[str, str]]:
    ports = []
    for port in list_ports.comports():
        ports.append(
            {
                "device": port.device,
                "name": port.name,
                "description": port.description,
                "hwid": port.hwid,
            }
        )
    if not ports:
        log_warning("NO_SERIAL_PORTS_DETECTED")
    return ports
