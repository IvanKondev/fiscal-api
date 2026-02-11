"""DatecsPay card reader (pinpad) communication protocol v1.9.

Packet format — completely different from Datecs fiscal protocol:
  EXT DEVICE → CARD READER:  '>' CMD 00 LH LL <DATA> CSUM
  CARD READER → EXT DEVICE:  '>' 00  ST LH LL <DATA> CSUM
  CSUM = XOR of all bytes in the packet (including 0x3E start byte).

Main commands:
  0x3D — Borica command (subcommands for transactions, info, reports)
  0x40 — External internet command (socket tunneling)

Async events from card reader:
  0x0E — Borica event (transaction complete, etc.)
  0x0F — External internet event (socket open/close/send data)
  0x0B — EMV event (user interface messages)
"""
from __future__ import annotations

import struct
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple

from app.app_logging import log_info, log_warning, log_error
from app.transports import BaseTransport


# ── Constants ──────────────────────────────────────────────────────────
START_BYTE = 0x3E          # '>'
CMD_BORICA = 0x3D
CMD_EXT_INTERNET = 0x40
EVT_BORICA = 0x0E
EVT_EXT_INTERNET = 0x0F
EVT_EMV = 0x0B

INTER_BYTE_TIMEOUT = 2.0   # seconds
RESPONSE_TIMEOUT = 5.0     # seconds
TRANSACTION_TIMEOUT = 120.0 # seconds — transactions can take long


# ── Borica subcommands ────────────────────────────────────────────────
class BorCmd(IntEnum):
    PING = 0x00
    TRANSACTION_START = 0x01
    GET_RECEIPT_TAGS = 0x02
    TRANSACTION_END = 0x03
    GET_REPORT_TAGS = 0x04
    GET_REPORT_INFO = 0x05
    GET_PINPAD_INFO = 0x06
    GET_RTC = 0x07
    SET_RTC = 0x08
    DELETE_BATCH = 0x0B
    CLEAR_REVERSAL = 0x0C
    GET_PINPAD_STATUS = 0x1A
    GET_MENU_INFO = 0x1D
    GET_PUBLIC_KEYS = 0x1E
    GET_SYMMETRIC_KEYS = 0x1F
    EDIT_COMM_PARAMS = 0x20
    KEYS_COMMAND = 0x21
    CHECK_PASSWORD = 0x23
    GET_REPORT_TAGS_BY_STAN = 0x24
    SELECT_CHIP_APP = 0x25
    GET_CARD_READER_STATE = 0x26
    GET_TERMINAL_TAGS = 0x27


# ── Transaction types ─────────────────────────────────────────────────
class TransType(IntEnum):
    PURCHASE = 0x01
    PURCHASE_CASHBACK = 0x02
    PURCHASE_REFERENCE = 0x03
    CASH_ADVANCE = 0x04
    AUTHORIZATION = 0x05
    PURCHASE_CODE = 0x06
    VOID_PURCHASE = 0x07
    VOID_CASH_ADVANCE = 0x08
    VOID_AUTHORIZATION = 0x09
    END_OF_DAY = 0x0A
    LOYALTY_BALANCE = 0x0B
    LOYALTY_SPEND = 0x0C
    VOID_LOYALTY_SPEND = 0x0D
    TEST_CONNECTION = 0x0E
    TMS_UPDATE = 0x0F


# ── Borica subevents ──────────────────────────────────────────────────
class BorEvent(IntEnum):
    TRANSACTION_COMPLETE = 0x01
    INTERMEDIATE_COMPLETE = 0x02
    PRINT_HANG_RECEIPT = 0x03
    SEND_LOG_DATA = 0x10
    SELECT_CHIP_APP = 0x3F


# ── External internet subevents ───────────────────────────────────────
class ExtEvent(IntEnum):
    SOCKET_OPEN = 0x01
    SOCKET_CLOSE = 0x02
    SEND_DATA = 0x03


# ── Error codes (ST field) ────────────────────────────────────────────
class ErrCode(IntEnum):
    NO_ERROR = 0x00
    GENERAL = 0x01
    INV_CMD = 0x02
    INV_PAR = 0x03
    INV_ADR = 0x04
    INV_VAL = 0x05
    INV_LEN = 0x06
    NO_PERMIT = 0x07
    NO_DATA = 0x08
    TIMEOUT = 0x09
    CANCEL = 0x12
    INV_PASS = 0x15
    BUSY = 0x26
    NOT_CONNECTED = 0x32
    USE_CHIP = 0x33
    END_DAY = 0x34


ERR_NAMES: Dict[int, str] = {
    0x00: "errNoErr", 0x01: "errGeneral", 0x02: "errInvCmd",
    0x03: "errInvPar", 0x04: "errInvAdr", 0x05: "errInvVal",
    0x06: "errInvLen", 0x07: "errNoPermit", 0x08: "errNoData",
    0x09: "errTimeOut", 0x0A: "errKeyNum", 0x0B: "errKeyAttr",
    0x0C: "errInvDevice", 0x0D: "errNoSupport", 0x0E: "errPinLimit",
    0x0F: "errFlash", 0x10: "errHard", 0x12: "errCancel",
    0x15: "errInvPass", 0x17: "errKeyFormat", 0x1F: "errNoPerm",
    0x26: "errBusy", 0x32: "errNoConnected", 0x33: "errUseChip",
    0x34: "errEndDay",
}


# ── TLV Tag definitions ───────────────────────────────────────────────
class Tag:
    AMOUNT = 0x81
    CASHBACK = 0x9F04
    RRN = 0xDF01
    AUTH_ID = 0xDF02
    REFERENCE = 0xDF03
    TIP = 0xDF63
    # Receipt / report tags
    TRANSACTION_RESULT = 0xDF05
    TRANSACTION_ERROR = 0xDF06
    HOST_RRN = 0xDF07
    HOST_AUTH_ID = 0xDF08
    HOST_CODE = 0xDF09
    CARD_SCHEME = 0xDF00
    MASKED_PAN = 0xDF0A
    CARDHOLDER_NAME = 0x5F20
    PAY_INTERFACE = 0xDF25
    CL_CARD_SCHEME = 0xDF60
    TRANS_TYPE = 0xDF10
    AMOUNT_EUR = 0xDF04
    CVM_SIGNATURE = 0xDF23
    EMV_STAN = 0x9F41
    TRANS_DATE = 0x9A
    TRANS_TIME = 0x9F21
    TERMINAL_ID = 0x9F1C
    MERCHANT_ID = 0x9F16
    MERCHANT_NAME_BG = 0xDF31
    MERCHANT_CITY_BG = 0xDF30
    MERCHANT_ADDR_BG = 0xDF2F
    MERCHANT_POST = 0xDF29
    MERCHANT_TITLE_BG = 0xDF2E
    MERCHANT_PHONE = 0xDF28
    BATCH_NUM = 0xDF61
    INTERFACE_ID = 0xDF62
    TERM_AID = 0x9F06
    APP_CRYPTOGRAM = 0x9F26
    ISSUER_ID = 0xDF79
    TO_TYPE = 0xDF12
    CURRENCY_NAME = 0xDF27
    CURRENCY_CODE = 0x5F2A
    IS_PIN_ENTERED = 0xDF7F
    TERMINAL_SN = 0x9F1E
    BATCH_NUMBER = 0xDF32
    LOYALTY_PTS = 0xDF0B
    MAX_CASHBACK_AMOUNT = 0xDF8004
    CASHBACK_CURRENCY = 0xDF8005
    BCARD_SCA_DECLINED = 0xDF8006

    # All tags needed for a full receipt
    RECEIPT_ALL = [
        0x81, 0x9F04, 0x9A, 0x9F21, 0x9F06, 0x9F26, 0x9F1C, 0x9F16,
        0x5F2A, 0x9F41, 0x5F20,
        0xDF00, 0xDF01, 0xDF02, 0xDF03, 0xDF04, 0xDF05, 0xDF06, 0xDF07,
        0xDF08, 0xDF09, 0xDF0A, 0xDF0B, 0xDF10, 0xDF12, 0xDF19, 0xDF23,
        0xDF25, 0xDF24, 0xDF26, 0xDF27, 0xDF28, 0xDF29, 0xDF2A, 0xDF2B,
        0xDF2C, 0xDF2D, 0xDF2E, 0xDF2F, 0xDF30, 0xDF31, 0xDF60, 0xDF61,
        0xDF62, 0xDF63, 0xDF64,
    ]


# ── Exceptions ─────────────────────────────────────────────────────────
class PinpadError(RuntimeError):
    """General pinpad communication error."""
    pass


class PinpadTimeoutError(PinpadError):
    """Timeout waiting for pinpad response."""
    pass


class PinpadStatusError(PinpadError):
    """Pinpad returned a non-zero status code."""
    def __init__(self, status: int, message: str = ""):
        self.status = status
        self.status_name = ERR_NAMES.get(status, f"unknown(0x{status:02X})")
        super().__init__(message or f"Pinpad error: {self.status_name} (0x{status:02X})")


# ── Data classes ───────────────────────────────────────────────────────
@dataclass
class PinpadResponse:
    """Response from card reader."""
    status: int
    data: bytes
    status_name: str = ""

    def __post_init__(self):
        self.status_name = ERR_NAMES.get(self.status, f"0x{self.status:02X}")

    @property
    def ok(self) -> bool:
        return self.status == ErrCode.NO_ERROR

    @property
    def no_data(self) -> bool:
        return self.status == ErrCode.NO_DATA


@dataclass
class PinpadEvent:
    """Async event from card reader."""
    event_type: int   # 0x0E, 0x0F, 0x0B
    subevent: int
    data: bytes


@dataclass
class PinpadInfo:
    """Parsed GET PINPAD INFO response."""
    model: str
    serial_number: str
    software_version: str
    terminal_id: str
    menu_type: int


@dataclass
class PinpadStatus:
    """Parsed GET PINPAD STATUS response."""
    reversal: int       # 0x00=none, 0x52='R'=reversal, 0x43='C'=hang
    end_day_required: bool

    @property
    def has_reversal(self) -> bool:
        return self.reversal == ord('R')

    @property
    def has_hang_transaction(self) -> bool:
        return self.reversal == ord('C')


@dataclass
class CardReaderState:
    """Parsed GET CARD READER STATE response."""
    state: int  # 1=idle, 2=transaction started, 3=select app, 4=PIN entry, 5=online auth

    STATE_NAMES = {1: "idle", 2: "transaction_started", 3: "select_application",
                   4: "pin_entry", 5: "online_authorization"}

    @property
    def name(self) -> str:
        return self.STATE_NAMES.get(self.state, f"unknown({self.state})")

    @property
    def is_idle(self) -> bool:
        return self.state == 1


@dataclass
class TransactionResult:
    """Parsed transaction result from TRANSACTION COMPLETE event + receipt tags."""
    approved: bool = False
    result_code: int = 0
    error_code: int = 0
    host_error_code: int = 0
    amount: int = 0                # in cents
    stan: int = 0                  # transaction sequence number
    rrn: str = ""
    auth_id: str = ""
    card_scheme: str = ""
    masked_pan: str = ""
    cardholder_name: str = ""
    terminal_id: str = ""
    merchant_id: str = ""
    merchant_name: str = ""
    trans_type: int = 0
    trans_date: str = ""
    trans_time: str = ""
    interface: int = 0             # 0=chip, 1=contactless, 2=magstripe, 3=manual
    batch_num: int = 0
    currency: str = ""
    all_tags: Dict[int, bytes] = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════
#  PACKET BUILD / PARSE
# ══════════════════════════════════════════════════════════════════════

def _xor_checksum(data: bytes) -> int:
    """XOR all bytes together."""
    csum = 0
    for b in data:
        csum ^= b
    return csum


def build_packet(cmd: int, data: bytes = b"") -> bytes:
    """Build EXT DEVICE → CARD READER packet.

    Format: '>' CMD 00 LH LL <DATA> CSUM
    """
    length = len(data)
    lh = (length >> 8) & 0xFF
    ll = length & 0xFF
    packet = bytes([START_BYTE, cmd, 0x00, lh, ll]) + data
    csum = _xor_checksum(packet)
    return packet + bytes([csum])


def parse_response_packet(raw: bytes) -> PinpadResponse:
    """Parse CARD READER → EXT DEVICE response.

    Format: '>' 00 ST LH LL <DATA> CSUM
    """
    if len(raw) < 6:
        raise PinpadError(f"Response too short: {len(raw)} bytes")
    if raw[0] != START_BYTE:
        raise PinpadError(f"Invalid start byte: 0x{raw[0]:02X}")
    if raw[1] != 0x00:
        raise PinpadError(f"Invalid fixed byte: 0x{raw[1]:02X}")
    st = raw[2]
    lh = raw[3]
    ll = raw[4]
    data_len = (lh << 8) | ll
    expected_len = 5 + data_len + 1  # header + data + CSUM
    if len(raw) < expected_len:
        raise PinpadError(f"Response incomplete: got {len(raw)}, expected {expected_len}")
    data = raw[5:5 + data_len]
    csum_received = raw[5 + data_len]
    csum_calc = _xor_checksum(raw[:5 + data_len])
    if csum_received != csum_calc:
        raise PinpadError(
            f"Checksum mismatch: received 0x{csum_received:02X}, "
            f"calculated 0x{csum_calc:02X}"
        )
    return PinpadResponse(status=st, data=data)


def parse_event_packet(raw: bytes) -> PinpadEvent:
    """Parse async event from CARD READER.

    Format: '>' EVT 00 LH LL <SUBEVENT> <DATA> CSUM
    """
    if len(raw) < 6:
        raise PinpadError(f"Event too short: {len(raw)} bytes")
    if raw[0] != START_BYTE:
        raise PinpadError(f"Invalid start byte: 0x{raw[0]:02X}")
    event_type = raw[1]
    # raw[2] = 0x00 fixed
    lh = raw[3]
    ll = raw[4]
    data_len = (lh << 8) | ll
    expected_len = 5 + data_len + 1
    if len(raw) < expected_len:
        raise PinpadError(f"Event incomplete: got {len(raw)}, expected {expected_len}")
    all_data = raw[5:5 + data_len]
    csum_received = raw[5 + data_len]
    csum_calc = _xor_checksum(raw[:5 + data_len])
    if csum_received != csum_calc:
        raise PinpadError(f"Event checksum mismatch")
    subevent = all_data[0] if all_data else 0
    event_data = all_data[1:] if len(all_data) > 1 else b""
    return PinpadEvent(event_type=event_type, subevent=subevent, data=event_data)


# ══════════════════════════════════════════════════════════════════════
#  TLV ENCODE / DECODE
# ══════════════════════════════════════════════════════════════════════

def encode_tag(tag: int) -> bytes:
    """Encode a TLV tag number to bytes (1, 2, or 3 byte tags)."""
    if tag <= 0xFF:
        return bytes([tag])
    elif tag <= 0xFFFF:
        return bytes([(tag >> 8) & 0xFF, tag & 0xFF])
    else:
        return bytes([(tag >> 16) & 0xFF, (tag >> 8) & 0xFF, tag & 0xFF])


def tlv_encode(tag: int, value: bytes) -> bytes:
    """Encode a single TLV element: Tag + Length + Value."""
    tag_bytes = encode_tag(tag)
    length = len(value)
    return tag_bytes + bytes([length]) + value


def tlv_amount(amount_cents: int) -> bytes:
    """Encode amount as TLV with tag 0x81, 4-byte big-endian."""
    return tlv_encode(Tag.AMOUNT, struct.pack(">I", amount_cents))


def tlv_cashback(amount_cents: int) -> bytes:
    """Encode cashback as TLV with tag 0x9F04, 4-byte big-endian."""
    return tlv_encode(Tag.CASHBACK, struct.pack(">I", amount_cents))


def tlv_tip(amount_cents: int) -> bytes:
    """Encode tip/gratuity as TLV with tag 0xDF63, 4-byte big-endian."""
    return tlv_encode(Tag.TIP, struct.pack(">I", amount_cents))


def tlv_rrn(rrn: str) -> bytes:
    """Encode RRN as TLV string with tag 0xDF01."""
    return tlv_encode(Tag.RRN, rrn.encode("ascii"))


def tlv_auth_id(auth_id: str) -> bytes:
    """Encode Authorization ID as TLV string with tag 0xDF02."""
    return tlv_encode(Tag.AUTH_ID, auth_id.encode("ascii"))


def tlv_reference(ref: str) -> bytes:
    """Encode reference as TLV string with tag 0xDF03."""
    return tlv_encode(Tag.REFERENCE, ref.encode("ascii"))


def encode_tags_list(tags: List[int]) -> bytes:
    """Encode a list of tag IDs (for GET RECEIPT TAGS / GET REPORT TAGS)."""
    result = bytearray()
    for tag in tags:
        result.extend(encode_tag(tag))
    return bytes(result)


def decode_tag(data: bytes, offset: int) -> Tuple[int, int]:
    """Decode tag number at offset. Returns (tag, new_offset)."""
    if offset >= len(data):
        raise PinpadError("TLV decode: unexpected end of data (tag)")
    b0 = data[offset]
    # 1-byte tag
    if b0 < 0x80:
        return b0, offset + 1
    # Multi-byte: check if next byte has high bit for 3-byte tag
    if offset + 1 >= len(data):
        return b0, offset + 1
    b1 = data[offset + 1]
    # 2-byte tag (0x9Fxx, 0xDFxx, 0x5Fxx)
    tag2 = (b0 << 8) | b1
    if offset + 2 < len(data) and b0 == 0xDF and b1 >= 0x80:
        # 3-byte tag (0xDFC1xx, 0xDF80xx)
        b2 = data[offset + 2]
        tag3 = (b0 << 16) | (b1 << 8) | b2
        return tag3, offset + 3
    return tag2, offset + 2


def tlv_decode(data: bytes) -> Dict[int, bytes]:
    """Decode TLV-encoded data into dict of {tag: value}."""
    result: Dict[int, bytes] = {}
    offset = 0
    while offset < len(data):
        try:
            tag, offset = decode_tag(data, offset)
            if offset >= len(data):
                break
            length = data[offset]
            offset += 1
            value = data[offset:offset + length]
            offset += length
            result[tag] = value
        except (IndexError, PinpadError):
            break
    return result


def tlv_get_int(tags: Dict[int, bytes], tag: int, default: int = 0) -> int:
    """Get an integer value from TLV tags (big-endian)."""
    val = tags.get(tag)
    if val is None:
        return default
    return int.from_bytes(val, "big")


def tlv_get_str(tags: Dict[int, bytes], tag: int, default: str = "") -> str:
    """Get a string value from TLV tags."""
    val = tags.get(tag)
    if val is None:
        return default
    return val.decode("ascii", errors="replace").rstrip("\x00")


def tlv_get_bcd(tags: Dict[int, bytes], tag: int, default: str = "") -> str:
    """Get a BCD-encoded value as string from TLV tags."""
    val = tags.get(tag)
    if val is None:
        return default
    return val.hex()


# ══════════════════════════════════════════════════════════════════════
#  LOW-LEVEL TRANSPORT I/O
# ══════════════════════════════════════════════════════════════════════

def _read_packet(transport: BaseTransport, timeout_s: float = RESPONSE_TIMEOUT) -> bytes:
    """Read a complete packet from the card reader.

    Waits for START_BYTE, then reads header to get length, then reads rest.
    """
    deadline = time.monotonic() + timeout_s
    buffer = bytearray()
    saw_start = False

    while time.monotonic() < deadline:
        chunk = transport.read(1)
        if not chunk:
            time.sleep(0.005)
            continue

        byte = chunk[0]
        if not saw_start:
            if byte != START_BYTE:
                continue
            saw_start = True
            buffer.append(byte)
            continue

        buffer.append(byte)

        # After we have header (5 bytes), we know the total length
        if len(buffer) >= 5:
            lh = buffer[3]
            ll = buffer[4]
            data_len = (lh << 8) | ll
            total_len = 5 + data_len + 1  # header + data + CSUM
            if len(buffer) >= total_len:
                return bytes(buffer)

    raise PinpadTimeoutError(
        f"Timeout ({timeout_s}s) waiting for pinpad response. "
        f"Received {len(buffer)} bytes so far."
    )


def send_command(
    transport: BaseTransport,
    cmd: int,
    data: bytes = b"",
    timeout_s: float = RESPONSE_TIMEOUT,
    correlation_id: str = "",
) -> PinpadResponse:
    """Send a command and wait for response."""
    packet = build_packet(cmd, data)
    log_info("PINPAD_SEND", {
        "cmd": f"0x{cmd:02X}",
        "data_hex": data.hex() if data else "",
        "packet_hex": packet.hex(),
        "packet_len": len(packet),
        "correlation_id": correlation_id,
    })
    transport.write(packet)
    raw = _read_packet(transport, timeout_s)
    response = parse_response_packet(raw)
    log_info("PINPAD_RECV", {
        "status": f"0x{response.status:02X}",
        "status_name": response.status_name,
        "data_hex": response.data.hex() if response.data else "",
        "data_len": len(response.data),
        "correlation_id": correlation_id,
    })
    return response


def read_event(
    transport: BaseTransport,
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> PinpadEvent:
    """Read an async event from the card reader."""
    raw = _read_packet(transport, timeout_s)
    event = parse_event_packet(raw)
    log_info("PINPAD_EVENT", {
        "event_type": f"0x{event.event_type:02X}",
        "subevent": f"0x{event.subevent:02X}",
        "data_len": len(event.data),
        "data_hex": event.data[:64].hex() if event.data else "",
        "correlation_id": correlation_id,
    })
    return event


def read_packet_any(
    transport: BaseTransport,
    timeout_s: float = TRANSACTION_TIMEOUT,
) -> bytes:
    """Read any packet (response or event) — raw bytes."""
    return _read_packet(transport, timeout_s)


# ══════════════════════════════════════════════════════════════════════
#  HIGH-LEVEL BORICA COMMANDS
# ══════════════════════════════════════════════════════════════════════

def borica_command(
    transport: BaseTransport,
    subcmd: int,
    data: bytes = b"",
    timeout_s: float = RESPONSE_TIMEOUT,
    correlation_id: str = "",
) -> PinpadResponse:
    """Send a Borica subcommand (CMD=0x3D)."""
    payload = bytes([subcmd]) + data
    return send_command(transport, CMD_BORICA, payload, timeout_s, correlation_id)


def ext_internet_command(
    transport: BaseTransport,
    subcmd: int,
    data: bytes = b"",
    timeout_s: float = RESPONSE_TIMEOUT,
    correlation_id: str = "",
) -> PinpadResponse:
    """Send an External Internet subcommand (CMD=0x40)."""
    payload = bytes([subcmd]) + data
    return send_command(transport, CMD_EXT_INTERNET, payload, timeout_s, correlation_id)


# ── Specific commands ─────────────────────────────────────────────────

def ping(transport: BaseTransport, correlation_id: str = "") -> bool:
    """Ping the card reader. Returns True if alive."""
    try:
        resp = borica_command(transport, BorCmd.PING, timeout_s=5.0,
                              correlation_id=correlation_id)
        return resp.ok
    except (PinpadError, PinpadTimeoutError):
        return False


def get_pinpad_info(transport: BaseTransport, correlation_id: str = "") -> PinpadInfo:
    """Get pinpad model, serial, software version, terminal ID."""
    resp = borica_command(transport, BorCmd.GET_PINPAD_INFO,
                          correlation_id=correlation_id)
    if not resp.ok:
        raise PinpadStatusError(resp.status, "GET PINPAD INFO failed")
    d = resp.data
    if len(d) < 43:
        raise PinpadError(f"GET PINPAD INFO response too short: {len(d)} bytes")
    model = d[0:20].decode("ascii", errors="replace").rstrip("\x00").strip()
    serial = d[20:30].decode("ascii", errors="replace").rstrip("\x00").strip()
    sv = d[30:34]
    sw_ver = f"{sv[0]}.{sv[1]}.{sv[2]}.{sv[3]}"
    terminal_id = d[34:42].decode("ascii", errors="replace").rstrip("\x00").strip()
    menu_type = d[42] if len(d) > 42 else 0
    return PinpadInfo(model=model, serial_number=serial, software_version=sw_ver,
                      terminal_id=terminal_id, menu_type=menu_type)


def get_pinpad_status(transport: BaseTransport, correlation_id: str = "") -> PinpadStatus:
    """Get reversal & end-of-day status."""
    resp = borica_command(transport, BorCmd.GET_PINPAD_STATUS,
                          correlation_id=correlation_id)
    if not resp.ok:
        raise PinpadStatusError(resp.status, "GET PINPAD STATUS failed")
    if len(resp.data) < 2:
        raise PinpadError("GET PINPAD STATUS response too short")
    return PinpadStatus(reversal=resp.data[0], end_day_required=resp.data[1] != 0)


def get_card_reader_state(transport: BaseTransport, correlation_id: str = "") -> CardReaderState:
    """Get card reader state (idle, transaction, PIN entry, etc.)."""
    resp = borica_command(transport, BorCmd.GET_CARD_READER_STATE,
                          correlation_id=correlation_id)
    if not resp.ok:
        raise PinpadStatusError(resp.status, "GET CARD READER STATE failed")
    if len(resp.data) < 1:
        raise PinpadError("GET CARD READER STATE response too short")
    return CardReaderState(state=resp.data[0])


def get_report_info(transport: BaseTransport, correlation_id: str = "") -> int:
    """Get count of records in the log. Returns record count."""
    resp = borica_command(transport, BorCmd.GET_REPORT_INFO,
                          correlation_id=correlation_id)
    if not resp.ok:
        raise PinpadStatusError(resp.status, "GET REPORT INFO failed")
    if len(resp.data) < 2:
        return 0
    return (resp.data[0] << 8) | resp.data[1]


def get_receipt_tags(
    transport: BaseTransport,
    tags: Optional[List[int]] = None,
    correlation_id: str = "",
) -> Dict[int, bytes]:
    """Get receipt tags for the last completed transaction."""
    tag_list = tags or Tag.RECEIPT_ALL
    tag_bytes = encode_tags_list(tag_list)
    resp = borica_command(transport, BorCmd.GET_RECEIPT_TAGS, tag_bytes,
                          timeout_s=5.0, correlation_id=correlation_id)
    if resp.no_data:
        return {}
    if not resp.ok:
        raise PinpadStatusError(resp.status, "GET RECEIPT TAGS failed")
    return tlv_decode(resp.data)


def transaction_end(
    transport: BaseTransport,
    success: bool = True,
    correlation_id: str = "",
) -> PinpadResponse:
    """Send TRANSACTION END. Must be called after every transaction."""
    cfm = bytes([0x00, 0x01]) if success else bytes([0x00, 0x00])
    return borica_command(transport, BorCmd.TRANSACTION_END, cfm,
                          correlation_id=correlation_id)


# ══════════════════════════════════════════════════════════════════════
#  TRANSACTION RESULT PARSING
# ══════════════════════════════════════════════════════════════════════

def parse_transaction_complete(event_data: bytes) -> TransactionResult:
    """Parse TRANSACTION COMPLETE event data (TLV-encoded)."""
    tags = tlv_decode(event_data)
    result = TransactionResult(
        result_code=tlv_get_int(tags, Tag.TRANSACTION_RESULT),
        error_code=tlv_get_int(tags, Tag.TRANSACTION_ERROR),
        amount=tlv_get_int(tags, Tag.AMOUNT),
        stan=tlv_get_int(tags, Tag.EMV_STAN),
        all_tags=tags,
    )
    result.approved = result.result_code == 0
    return result


def enrich_with_receipt_tags(result: TransactionResult, receipt_tags: Dict[int, bytes]) -> TransactionResult:
    """Enrich TransactionResult with receipt tag data."""
    result.all_tags.update(receipt_tags)
    tags = result.all_tags
    result.rrn = tlv_get_str(tags, Tag.HOST_RRN)
    result.auth_id = tlv_get_str(tags, Tag.HOST_AUTH_ID)
    result.host_error_code = tlv_get_int(tags, Tag.HOST_CODE)
    result.card_scheme = tlv_get_str(tags, Tag.CARD_SCHEME)
    result.masked_pan = tlv_get_str(tags, Tag.MASKED_PAN)
    result.cardholder_name = tlv_get_str(tags, Tag.CARDHOLDER_NAME)
    result.terminal_id = tlv_get_str(tags, Tag.TERMINAL_ID)
    result.merchant_id = tlv_get_str(tags, Tag.MERCHANT_ID)
    result.merchant_name = tlv_get_str(tags, Tag.MERCHANT_NAME_BG)
    result.trans_type = tlv_get_int(tags, Tag.TRANS_TYPE)
    result.interface = tlv_get_int(tags, Tag.PAY_INTERFACE)
    result.batch_num = tlv_get_int(tags, Tag.BATCH_NUM)
    result.currency = tlv_get_str(tags, Tag.CURRENCY_NAME)
    result.amount = tlv_get_int(tags, Tag.AMOUNT) or result.amount
    # BCD date/time
    date_raw = tags.get(Tag.TRANS_DATE)
    if date_raw and len(date_raw) == 3:
        result.trans_date = f"20{date_raw[0]:02X}-{date_raw[1]:02X}-{date_raw[2]:02X}"
    time_raw = tags.get(Tag.TRANS_TIME)
    if time_raw and len(time_raw) == 3:
        result.trans_time = f"{time_raw[0]:02X}:{time_raw[1]:02X}:{time_raw[2]:02X}"
    return result
