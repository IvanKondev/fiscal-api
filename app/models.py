from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class PrinterBase(BaseModel):
    name: str
    model: str
    transport: str
    port: Optional[str] = None
    baudrate: int = 9600
    data_bits: int = 8
    parity: str = "N"
    stop_bits: float = 1
    timeout_ms: int = 5000
    ip_address: Optional[str] = None
    tcp_port: int = 4999
    enabled: bool = True
    dry_run: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)
    serial_number: Optional[str] = None
    firmware: Optional[str] = None
    fiscal_memory_number: Optional[str] = None


class PrinterCreate(PrinterBase):
    pass


class PrinterUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    transport: Optional[str] = None
    port: Optional[str] = None
    baudrate: Optional[int] = None
    data_bits: Optional[int] = None
    parity: Optional[str] = None
    stop_bits: Optional[float] = None
    timeout_ms: Optional[int] = None
    ip_address: Optional[str] = None
    tcp_port: Optional[int] = None
    enabled: Optional[bool] = None
    dry_run: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    serial_number: Optional[str] = None
    firmware: Optional[str] = None
    fiscal_memory_number: Optional[str] = None


class PrinterOut(PrinterBase):
    id: int
    serial_number: Optional[str] = None
    firmware: Optional[str] = None
    fiscal_memory_number: Optional[str] = None
    created_at: str
    updated_at: str


class JobCreate(BaseModel):
    printer_id: int
    payload_type: Literal[
        "text",
        "receipt",
        "fiscal_receipt",
        "storno",
        "report",
        "cash",
        "pinpad_purchase",
        "pinpad_void",
        "pinpad_end_of_day",
        "pinpad_test",
        "pinpad_info",
        "pinpad_status",
        "pinpad_ping",
    ]
    payload: Dict[str, Any]


class JobOut(BaseModel):
    id: int
    printer_id: int
    payload_type: str
    payload: Dict[str, Any]
    status: str
    retries: int
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class LogOut(BaseModel):
    id: int
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None
    created_at: str
