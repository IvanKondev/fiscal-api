"""DatecsPay pinpad high-level operations.

Handles full transaction flows including the event loop for socket proxying
when the card reader doesn't have its own internet connectivity.
"""
from __future__ import annotations

import socket
import time
import uuid
from dataclasses import asdict
from typing import Any, Dict, Optional

from app.app_logging import log_info, log_warning, log_error
from app.transports import BaseTransport
from app.datecspay_protocol import (
    # Constants
    START_BYTE, CMD_BORICA, CMD_EXT_INTERNET,
    EVT_BORICA, EVT_EXT_INTERNET, EVT_EMV,
    TRANSACTION_TIMEOUT,
    # Enums
    BorCmd, TransType, BorEvent, ExtEvent, ErrCode,
    # Data classes
    PinpadResponse, PinpadEvent, PinpadInfo, PinpadStatus,
    CardReaderState, TransactionResult,
    # Packet funcs
    build_packet, parse_response_packet, parse_event_packet,
    read_packet_any,
    # TLV
    Tag, tlv_amount, tlv_cashback, tlv_tip, tlv_rrn, tlv_auth_id,
    tlv_reference, encode_tags_list, tlv_decode,
    # High-level commands
    borica_command, ext_internet_command,
    ping, get_pinpad_info, get_pinpad_status, get_card_reader_state,
    get_report_info, get_receipt_tags, transaction_end,
    parse_transaction_complete, enrich_with_receipt_tags,
    # Exceptions
    PinpadError, PinpadTimeoutError, PinpadStatusError,
)


# ══════════════════════════════════════════════════════════════════════
#  SOCKET PROXY — for card readers without own internet
# ══════════════════════════════════════════════════════════════════════

class _SocketProxy:
    """Manages TCP sockets on behalf of the card reader."""

    def __init__(self):
        self._sockets: Dict[int, socket.socket] = {}

    def open_socket(self, sock_id: int, addr: str, port: int,
                    timeout: int, sock_type: int = 1) -> bool:
        """Open a TCP socket. Returns True on success."""
        try:
            if sock_type in (1, 3):  # TCP or TCP TLS
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(timeout)
            s.connect((addr, port))
            self._sockets[sock_id] = s
            log_info("PINPAD_SOCKET_OPEN", {
                "id": sock_id, "addr": addr, "port": port, "type": sock_type
            })
            return True
        except Exception as e:
            log_error("PINPAD_SOCKET_OPEN_FAIL", {
                "id": sock_id, "addr": addr, "port": port, "error": str(e)
            })
            return False

    def close_socket(self, sock_id: int) -> bool:
        s = self._sockets.pop(sock_id, None)
        if s:
            try:
                s.close()
            except Exception:
                pass
            log_info("PINPAD_SOCKET_CLOSE", {"id": sock_id})
            return True
        return False

    def send_data(self, sock_id: int, data: bytes) -> bool:
        s = self._sockets.get(sock_id)
        if not s:
            log_error("PINPAD_SOCKET_SEND_NO_SOCKET", {"id": sock_id})
            return False
        try:
            s.sendall(data)
            log_info("PINPAD_SOCKET_SEND", {"id": sock_id, "len": len(data)})
            return True
        except Exception as e:
            log_error("PINPAD_SOCKET_SEND_FAIL", {"id": sock_id, "error": str(e)})
            return False

    def receive_data(self, sock_id: int, timeout: float = 0.1) -> Optional[bytes]:
        s = self._sockets.get(sock_id)
        if not s:
            return None
        try:
            s.settimeout(timeout)
            data = s.recv(4096)
            if data:
                log_info("PINPAD_SOCKET_RECV", {"id": sock_id, "len": len(data)})
            return data if data else None
        except socket.timeout:
            return None
        except Exception:
            return None

    def close_all(self):
        for sid in list(self._sockets.keys()):
            self.close_socket(sid)


# ══════════════════════════════════════════════════════════════════════
#  TRANSACTION FLOW ENGINE
# ══════════════════════════════════════════════════════════════════════

def _handle_ext_event(
    transport: BaseTransport,
    event: PinpadEvent,
    proxy: _SocketProxy,
    mtu: int = 0x0400,
    correlation_id: str = "",
) -> None:
    """Handle an External Internet subevent."""
    if event.subevent == ExtEvent.SOCKET_OPEN:
        # Parse: [ID] [TYPE] <ADDRESS:4> <PORT:2> <TIMEOUT:2> [TLV...]
        d = event.data
        sock_id = d[0]
        sock_type = d[1]
        addr = f"{d[2]}.{d[3]}.{d[4]}.{d[5]}"
        port = (d[6] << 8) | d[7]
        timeout = (d[8] << 8) | d[9]
        success = proxy.open_socket(sock_id, addr, port, timeout, sock_type)
        # Send EVENT CONFIRM
        confirm_data = bytes([0x01, 0x00 if success else 0x01])
        # Add MTU
        confirm_data += bytes([(mtu >> 8) & 0xFF, mtu & 0xFF])
        ext_internet_command(transport, 0x02, confirm_data,
                             correlation_id=correlation_id)

    elif event.subevent == ExtEvent.SOCKET_CLOSE:
        sock_id = event.data[0] if event.data else 0
        proxy.close_socket(sock_id)
        # Send EVENT CONFIRM
        confirm_data = bytes([0x02, 0x00])
        ext_internet_command(transport, 0x02, confirm_data,
                             correlation_id=correlation_id)

    elif event.subevent == ExtEvent.SEND_DATA:
        sock_id = event.data[0] if event.data else 0
        send_data = event.data[1:] if len(event.data) > 1 else b""
        success = proxy.send_data(sock_id, send_data)
        # Send EVENT CONFIRM
        confirm_data = bytes([0x03, 0x00 if success else 0x01])
        ext_internet_command(transport, 0x02, confirm_data,
                             correlation_id=correlation_id)

        # Now we need to check if host sent back any data
        # and forward it to the card reader
        time.sleep(0.05)
        _forward_host_data(transport, proxy, sock_id, mtu, correlation_id)


def _forward_host_data(
    transport: BaseTransport,
    proxy: _SocketProxy,
    sock_id: int,
    mtu: int = 0x0400,
    correlation_id: str = "",
) -> None:
    """Check for data from host and forward to card reader."""
    data = proxy.receive_data(sock_id, timeout=5.0)
    if not data:
        return

    # Split into MTU-sized chunks
    offset = 0
    while offset < len(data):
        chunk = data[offset:offset + mtu]
        offset += mtu
        # Send RECEIVE DATA (subcmd 0x01)
        payload = bytes([sock_id]) if False else b""  # sock_id not in payload per spec
        resp = ext_internet_command(
            transport, 0x01, chunk,
            timeout_s=5.0,
            correlation_id=correlation_id,
        )
        # If busy, retry with 100ms delay
        while resp.status == ErrCode.BUSY:
            time.sleep(0.1)
            resp = ext_internet_command(
                transport, 0x01, chunk,
                timeout_s=5.0,
                correlation_id=correlation_id,
            )


def _transaction_loop(
    transport: BaseTransport,
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> TransactionResult:
    """Run the transaction event loop until TRANSACTION COMPLETE.

    Handles:
    - Borica events (transaction complete, intermediate, hang receipt)
    - External internet events (socket open/close/send data)
    - EMV events (user interface messages)
    - Forwarding host data to card reader
    """
    proxy = _SocketProxy()
    result = TransactionResult()
    deadline = time.monotonic() + timeout_s

    try:
        while time.monotonic() < deadline:
            # Check for incoming data from open sockets
            for sock_id in list(proxy._sockets.keys()):
                host_data = proxy.receive_data(sock_id, timeout=0.05)
                if host_data:
                    # Forward to card reader via RECEIVE DATA
                    resp = ext_internet_command(
                        transport, 0x01, host_data,
                        timeout_s=5.0,
                        correlation_id=correlation_id,
                    )
                    while resp.status == ErrCode.BUSY:
                        time.sleep(0.1)
                        resp = ext_internet_command(
                            transport, 0x01, host_data,
                            timeout_s=5.0,
                            correlation_id=correlation_id,
                        )

            # Read next packet from card reader
            try:
                raw = read_packet_any(transport, timeout_s=1.0)
            except PinpadTimeoutError:
                continue

            if len(raw) < 6:
                continue

            pkt_type = raw[1]  # second byte determines type

            if pkt_type == 0x00:
                # This is a response to our command (shouldn't happen here normally)
                continue

            elif pkt_type == EVT_BORICA:
                event = parse_event_packet(raw)
                log_info("PINPAD_BORICA_EVENT", {
                    "subevent": f"0x{event.subevent:02X}",
                    "data_len": len(event.data),
                    "correlation_id": correlation_id,
                })
                if event.subevent == BorEvent.TRANSACTION_COMPLETE:
                    result = parse_transaction_complete(event.data)
                    return result
                elif event.subevent == BorEvent.INTERMEDIATE_COMPLETE:
                    # Hung transaction completed before ours
                    log_warning("PINPAD_INTERMEDIATE_COMPLETE", {
                        "data_hex": event.data.hex(),
                        "correlation_id": correlation_id,
                    })
                elif event.subevent == BorEvent.PRINT_HANG_RECEIPT:
                    log_warning("PINPAD_HANG_RECEIPT", {
                        "data_len": len(event.data),
                        "correlation_id": correlation_id,
                    })

            elif pkt_type == EVT_EXT_INTERNET:
                event = parse_event_packet(raw)
                _handle_ext_event(transport, event, proxy,
                                  correlation_id=correlation_id)

            elif pkt_type == EVT_EMV:
                event = parse_event_packet(raw)
                log_info("PINPAD_EMV_EVENT", {
                    "subevent": f"0x{event.subevent:02X}",
                    "data_hex": event.data.hex() if event.data else "",
                    "correlation_id": correlation_id,
                })

        raise PinpadTimeoutError(f"Transaction timeout ({timeout_s}s)")

    finally:
        proxy.close_all()


# ══════════════════════════════════════════════════════════════════════
#  PUBLIC TRANSACTION OPERATIONS
# ══════════════════════════════════════════════════════════════════════

def purchase(
    transport: BaseTransport,
    amount_cents: int,
    tip_cents: int = 0,
    cashback_cents: int = 0,
    reference: str = "",
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> TransactionResult:
    """Execute a card purchase transaction.

    Args:
        amount_cents: Amount in cents (100 = 1.00 BGN).
                      For tip: total amount including tip.
                      For cashback: amount WITHOUT cashback.
        tip_cents: Optional tip/gratuity in cents.
        cashback_cents: Optional cashback in cents.
        reference: Optional reference string.
    """
    cid = correlation_id or uuid.uuid4().hex[:16]

    # Build transaction params
    if tip_cents > 0:
        trans_type = TransType.PURCHASE
        params = tlv_amount(amount_cents) + tlv_tip(tip_cents)
    elif cashback_cents > 0:
        trans_type = TransType.PURCHASE_CASHBACK
        params = tlv_amount(amount_cents) + tlv_cashback(cashback_cents)
    elif reference:
        trans_type = TransType.PURCHASE_REFERENCE
        params = tlv_amount(amount_cents) + tlv_reference(reference)
    else:
        trans_type = TransType.PURCHASE
        params = tlv_amount(amount_cents)

    # Start transaction
    data = bytes([trans_type]) + params
    resp = borica_command(transport, BorCmd.TRANSACTION_START, data,
                          timeout_s=5.0, correlation_id=cid)
    if not resp.ok:
        raise PinpadStatusError(resp.status, f"PURCHASE start failed: {resp.status_name}")

    # Transaction loop — wait for completion
    result = _transaction_loop(transport, timeout_s, cid)

    # Get receipt tags
    try:
        receipt = get_receipt_tags(transport, correlation_id=cid)
        if receipt:
            result = enrich_with_receipt_tags(result, receipt)
    except PinpadError as e:
        log_warning("PINPAD_RECEIPT_TAGS_FAIL", {"error": str(e), "correlation_id": cid})

    # End transaction
    try:
        transaction_end(transport, success=result.approved, correlation_id=cid)
    except PinpadError as e:
        log_warning("PINPAD_TRANS_END_FAIL", {"error": str(e), "correlation_id": cid})

    return result


def void_purchase(
    transport: BaseTransport,
    amount_cents: int,
    rrn: str,
    auth_id: str,
    tip_cents: int = 0,
    cashback_cents: int = 0,
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> TransactionResult:
    """Void a previous purchase transaction."""
    cid = correlation_id or uuid.uuid4().hex[:16]

    params = tlv_amount(amount_cents) + tlv_rrn(rrn) + tlv_auth_id(auth_id)
    if tip_cents > 0:
        params += tlv_tip(tip_cents)
    if cashback_cents > 0:
        params += tlv_cashback(cashback_cents)

    data = bytes([TransType.VOID_PURCHASE]) + params
    resp = borica_command(transport, BorCmd.TRANSACTION_START, data,
                          timeout_s=5.0, correlation_id=cid)
    if not resp.ok:
        raise PinpadStatusError(resp.status, f"VOID start failed: {resp.status_name}")

    result = _transaction_loop(transport, timeout_s, cid)

    try:
        receipt = get_receipt_tags(transport, correlation_id=cid)
        if receipt:
            result = enrich_with_receipt_tags(result, receipt)
    except PinpadError:
        pass

    try:
        transaction_end(transport, success=result.approved, correlation_id=cid)
    except PinpadError:
        pass

    return result


def end_of_day(
    transport: BaseTransport,
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> TransactionResult:
    """Execute End of Day (settlement)."""
    cid = correlation_id or uuid.uuid4().hex[:16]

    data = bytes([TransType.END_OF_DAY])
    resp = borica_command(transport, BorCmd.TRANSACTION_START, data,
                          timeout_s=5.0, correlation_id=cid)
    if not resp.ok:
        raise PinpadStatusError(resp.status, f"END OF DAY start failed: {resp.status_name}")

    result = _transaction_loop(transport, timeout_s, cid)

    try:
        transaction_end(transport, success=result.approved, correlation_id=cid)
    except PinpadError:
        pass

    return result


def test_connection(
    transport: BaseTransport,
    timeout_s: float = TRANSACTION_TIMEOUT,
    correlation_id: str = "",
) -> TransactionResult:
    """Execute a test connection to the Borica host."""
    cid = correlation_id or uuid.uuid4().hex[:16]

    data = bytes([TransType.TEST_CONNECTION])
    resp = borica_command(transport, BorCmd.TRANSACTION_START, data,
                          timeout_s=5.0, correlation_id=cid)
    if not resp.ok:
        raise PinpadStatusError(resp.status, f"TEST CONNECTION start failed: {resp.status_name}")

    result = _transaction_loop(transport, timeout_s, cid)

    try:
        transaction_end(transport, success=result.approved, correlation_id=cid)
    except PinpadError:
        pass

    return result


# ══════════════════════════════════════════════════════════════════════
#  JOB DISPATCHER — called from job_queue for pinpad operations
# ══════════════════════════════════════════════════════════════════════

def pinpad_operation(
    transport: BaseTransport,
    payload: Dict[str, Any],
    payload_type: str,
    printer: Dict[str, Any],
    correlation_id: str = "",
) -> Dict[str, Any]:
    """Dispatch a pinpad operation based on payload_type.

    Supported payload_types:
    - pinpad_purchase: Card payment
    - pinpad_void: Void a previous purchase
    - pinpad_end_of_day: Settlement
    - pinpad_test: Test connection
    - pinpad_info: Get device info
    - pinpad_status: Get device status
    """
    cid = correlation_id or uuid.uuid4().hex[:16]

    if payload_type == "pinpad_info":
        info = get_pinpad_info(transport, cid)
        return {
            "model": info.model,
            "serial_number": info.serial_number,
            "software_version": info.software_version,
            "terminal_id": info.terminal_id,
            "menu_type": info.menu_type,
            "correlation_id": cid,
        }

    elif payload_type == "pinpad_status":
        status = get_pinpad_status(transport, cid)
        state = get_card_reader_state(transport, cid)
        report_count = get_report_info(transport, cid)
        return {
            "has_reversal": status.has_reversal,
            "has_hang_transaction": status.has_hang_transaction,
            "end_day_required": status.end_day_required,
            "reader_state": state.name,
            "report_count": report_count,
            "correlation_id": cid,
        }

    elif payload_type == "pinpad_purchase":
        amount = payload.get("amount", 0)
        if isinstance(amount, float):
            amount_cents = int(round(amount * 100))
        else:
            amount_cents = int(amount)
        tip = payload.get("tip", 0)
        tip_cents = int(round(float(tip) * 100)) if tip else 0
        cashback = payload.get("cashback", 0)
        cashback_cents = int(round(float(cashback) * 100)) if cashback else 0
        reference = payload.get("reference", "")

        result = purchase(transport, amount_cents, tip_cents, cashback_cents,
                          reference, correlation_id=cid)
        return _result_to_dict(result, cid)

    elif payload_type == "pinpad_void":
        amount = payload.get("amount", 0)
        if isinstance(amount, float):
            amount_cents = int(round(amount * 100))
        else:
            amount_cents = int(amount)
        rrn_val = payload.get("rrn", "")
        auth_id_val = payload.get("auth_id", "")
        if not rrn_val or not auth_id_val:
            raise PinpadError("Void requires 'rrn' and 'auth_id' from original purchase")

        result = void_purchase(transport, amount_cents, rrn_val, auth_id_val,
                               correlation_id=cid)
        return _result_to_dict(result, cid)

    elif payload_type == "pinpad_end_of_day":
        result = end_of_day(transport, correlation_id=cid)
        return _result_to_dict(result, cid)

    elif payload_type == "pinpad_test":
        result = test_connection(transport, correlation_id=cid)
        return _result_to_dict(result, cid)

    elif payload_type == "pinpad_ping":
        alive = ping(transport, cid)
        return {"alive": alive, "correlation_id": cid}

    else:
        raise PinpadError(f"Unknown pinpad operation: {payload_type}")


def _result_to_dict(result: TransactionResult, correlation_id: str) -> Dict[str, Any]:
    """Convert TransactionResult to JSON-serializable dict."""
    return {
        "approved": result.approved,
        "result_code": result.result_code,
        "error_code": result.error_code,
        "host_error_code": result.host_error_code,
        "amount": result.amount,
        "amount_display": f"{result.amount / 100:.2f}" if result.amount else "0.00",
        "stan": result.stan,
        "rrn": result.rrn,
        "auth_id": result.auth_id,
        "card_scheme": result.card_scheme,
        "masked_pan": result.masked_pan,
        "cardholder_name": result.cardholder_name,
        "terminal_id": result.terminal_id,
        "merchant_id": result.merchant_id,
        "merchant_name": result.merchant_name,
        "trans_type": result.trans_type,
        "trans_date": result.trans_date,
        "trans_time": result.trans_time,
        "interface": result.interface,
        "batch_num": result.batch_num,
        "currency": result.currency,
        "correlation_id": correlation_id,
    }
