from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from app.app_logging import log_warning
from app.transports import BaseTransport

PRE = 0x01
PST = 0x05
EOT = 0x03
SEP = 0x04
NAK = 0x15
SYN = 0x16

SEQ_MIN = 0x20
SEQ_MAX = 0xFF


@dataclass
class DatecsResponse:
    cmd: int
    seq: int
    data: bytes
    fields: List[str]
    status: bytes


class DatecsProtocolError(RuntimeError):
    pass


class DatecsTimeoutError(DatecsProtocolError):
    pass


def _encode_nibbles(value: int) -> bytes:
    if value < 0 or value > 0xFFFF:
        raise ValueError("Value out of range for nibble encoding")
    return bytes(
        [
            0x30 + ((value >> 12) & 0xF),
            0x30 + ((value >> 8) & 0xF),
            0x30 + ((value >> 4) & 0xF),
            0x30 + (value & 0xF),
        ]
    )


def _decode_nibbles(data: bytes) -> int:
    if len(data) != 4:
        raise ValueError("Nibble data must be 4 bytes")
    value = 0
    for byte in data:
        digit = byte - 0x30
        if digit < 0 or digit > 0xF:
            raise ValueError("Invalid nibble encoding")
        value = (value << 4) | digit
    return value


def build_request(
    cmd: int,
    data: bytes | None = None,
    seq: int = SEQ_MIN,
    protocol_format: str = "hex4",
) -> bytes:
    payload = data or b""
    if protocol_format == "byte":
        length_value = 0x20 + 4 + len(payload)
        length_bytes = bytes([length_value & 0xFF])
        cmd_bytes = bytes([cmd & 0xFF])
    else:
        length_value = 0x20 + 10 + len(payload)
        length_bytes = _encode_nibbles(length_value)
        cmd_bytes = _encode_nibbles(cmd)
    body = length_bytes + bytes([seq]) + cmd_bytes + payload + bytes([PST])
    bcc = _encode_nibbles(sum(body) & 0xFFFF)
    return bytes([PRE]) + body + bcc + bytes([EOT])


def parse_response(buffer: bytes, protocol_format: str = "hex4", status_length: int = 8) -> DatecsResponse:
    if not buffer or buffer[0] != PRE:
        raise DatecsProtocolError("Invalid response preamble")
    if protocol_format == "byte":
        length_value = buffer[1]
        length_total = length_value - 0x20
    else:
        length_value = _decode_nibbles(buffer[1:5])
        length_total = length_value - 0x20
    expected_total = 1 + length_total + 4 + 1
    if len(buffer) < expected_total:
        raise DatecsProtocolError("Response length is incomplete")
    body = buffer[1 : 1 + length_total]
    bcc_bytes = buffer[1 + length_total : 1 + length_total + 4]
    bcc_expected = _decode_nibbles(bcc_bytes)
    bcc_actual = sum(body) & 0xFFFF
    if bcc_actual != bcc_expected:
        raise DatecsProtocolError("BCC checksum mismatch")
    if protocol_format == "byte":
        seq = body[1]
        cmd = body[2]
        base_len = 5 + status_length
        data_len = length_total - base_len
        if data_len < 0:
            raise DatecsProtocolError("Invalid response length")
        data = body[3 : 3 + data_len]
        sep = body[3 + data_len]
        if sep != SEP:
            log_warning("DATECS_RESPONSE_SEP_MISMATCH", {"sep": sep})
        status = body[4 + data_len : 4 + data_len + status_length]
        pst = body[-1]
    else:
        seq = body[4]
        cmd = _decode_nibbles(body[5:9])
        base_len = 11 + status_length
        data_len = length_total - base_len
        if data_len < 0:
            raise DatecsProtocolError("Invalid response length")
        data = body[9 : 9 + data_len]
        sep = body[9 + data_len]
        if sep != SEP:
            log_warning("DATECS_RESPONSE_SEP_MISMATCH", {"sep": sep})
        status = body[10 + data_len : 10 + data_len + status_length]
        pst = body[-1]
    if data_len < 0:
        raise DatecsProtocolError("Invalid response length")
    if pst != PST:
        raise DatecsProtocolError("Invalid response postamble")
    fields = _decode_fields(data)
    return DatecsResponse(cmd=cmd, seq=seq, data=data, fields=fields, status=status)


def _decode_fields(data: bytes) -> List[str]:
    if not data:
        return []
    parts = data.split(b"\t")
    decoded: List[str] = []
    for part in parts:
        if part == b"":
            decoded.append("")
        else:
            try:
                decoded.append(part.decode("cp1251"))
            except UnicodeDecodeError:
                decoded.append(part.decode("latin-1", errors="ignore"))
    return decoded


def read_response(
    transport: BaseTransport,
    timeout_s: float = 1.0,
    protocol_format: str = "hex4",
    status_length: int = 8,
) -> DatecsResponse:
    deadline = time.monotonic() + timeout_s
    buffer = bytearray()
    saw_preamble = False
    while time.monotonic() < deadline:
        chunk = transport.read(1)
        if not chunk:
            time.sleep(0.001)
            continue
        byte = chunk[0]
        if not saw_preamble:
            if byte == NAK:
                raise DatecsProtocolError("NAK received.")
            if byte == SYN:
                deadline = time.monotonic() + timeout_s
                continue
            if byte != PRE:
                continue
            saw_preamble = True
        buffer.append(byte)
        if byte == EOT:
            return parse_response(bytes(buffer), protocol_format=protocol_format, status_length=status_length)
    raise DatecsProtocolError(
        f"Timeout waiting for Datecs response after {timeout_s}s. "
        f"Check: 1) Printer is ON, 2) Correct COM port, 3) Correct baudrate (try 9600, 19200, 38400, 57600, 115200), "
        f"4) Cable is connected, 5) No other software is using the port."
    )


def send_command(
    transport: BaseTransport,
    cmd: int,
    data: bytes | None = None,
    seq: int = SEQ_MIN,
    timeout_s: float = 1.0,
    retries: int = 2,
    protocol_format: str = "hex4",
    status_length: int = 8,
) -> DatecsResponse:
    from app.app_logging import log_info, log_error
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        frame = build_request(cmd, data=data, seq=seq, protocol_format=protocol_format)
        log_info("DATECS_PROTOCOL_SEND", {
            "attempt": attempt + 1,
            "cmd": f"0x{cmd:02X}",
            "seq": f"0x{seq:02X}",
            "frame_hex": frame.hex(),
            "frame_len": len(frame),
            "protocol_format": protocol_format,
        })
        transport.write(frame)
        try:
            response = read_response(
                transport,
                timeout_s=timeout_s,
                protocol_format=protocol_format,
                status_length=status_length,
            )
            log_info("DATECS_PROTOCOL_RECV", {
                "cmd": f"0x{cmd:02X}",
                "seq": f"0x{seq:02X}",
                "status_hex": response.status.hex(),
                "fields_count": len(response.fields),
            })
            return response
        except DatecsProtocolError as exc:
            log_error("DATECS_PROTOCOL_ERROR", {
                "attempt": attempt + 1,
                "cmd": f"0x{cmd:02X}",
                "error": str(exc),
            })
            last_error = exc
            continue
    raise last_error or DatecsProtocolError("No response from printer.")


def next_seq(current: int) -> int:
    if current < SEQ_MIN or current >= SEQ_MAX:
        return SEQ_MIN
    return current + 1
