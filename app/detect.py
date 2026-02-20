"""Auto-detect Datecs printer model on a COM port.

Sends command 0x5A (Diagnostic Information) using both protocol formats
(hex4 for FP-700 series, byte for FP-2000 series) at common baudrates.
Parses the response to identify the exact printer model.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import serial as serial_lib

from app.app_logging import log_error, log_info
from app.datecs_protocol import (
    DatecsProtocolError,
    build_request,
    read_response,
)
from app.transports import BaseTransport
from app.transports.serial_transport import SerialConfig, SerialTransport
from app.transports.tcp_transport import TcpConfig, TcpTransport

CMD_DIAGNOSTIC = 0x5A
SEQ = 0x20
DETECT_TIMEOUT_S = 1.5

COMMON_BAUDRATES = [115200, 9600, 57600, 38400, 19200]

# Map diagnostic Name → adapter model key
# FP-700 series (hex4 protocol) — Name returned in fields[1]
# FP-2000 series (byte protocol) — Name returned in fields[0] comma-separated
_NAME_TO_MODEL: dict[str, str] = {
    "FP-700MX": "datecs_fp700mx",
    "FP700MX": "datecs_fp700mx",
    "FP-700X": "datecs_fp700x",
    "FP700X": "datecs_fp700x",
    "FP-700XE": "datecs_fp700xe",
    "FP700XE": "datecs_fp700xe",
    "FMP-350X": "datecs_fmp350x",
    "FMP350X": "datecs_fmp350x",
    "FMP-55X": "datecs_fmp55x",
    "FMP55X": "datecs_fmp55x",
    "WP-500X": "datecs_wp500x",
    "WP500X": "datecs_wp500x",
    "WP-50X": "datecs_wp50x",
    "WP50X": "datecs_wp50x",
    "WP-25X": "datecs_wp25x",
    "WP25X": "datecs_wp25x",
    "DP-25X": "datecs_dp25x",
    "DP25X": "datecs_dp25x",
    "DP-150X": "datecs_dp150x",
    "DP150X": "datecs_dp150x",
    "DP-05C": "datecs_dp05c",
    "DP05C": "datecs_dp05c",
    "FP-2000": "datecs_fp2000",
    "FP2000": "datecs_fp2000",
    "FP-800": "datecs_fp800",
    "FP800": "datecs_fp800",
    "FP-650": "datecs_fp650",
    "FP650": "datecs_fp650",
    "SK1-21F": "datecs_sk1_21f",
    "SK121F": "datecs_sk1_21f",
    "SK1-31F": "datecs_sk1_31f",
    "SK131F": "datecs_sk1_31f",
    "FMP-10": "datecs_fmp10",
    "FMP10": "datecs_fmp10",
    "FP-700": "datecs_fp700",
    "FP700": "datecs_fp700",
}


def _match_model(name: str) -> Optional[str]:
    """Match a diagnostic name string to an adapter model key."""
    clean = name.strip()
    # Direct match
    if clean in _NAME_TO_MODEL:
        return _NAME_TO_MODEL[clean]
    # Case-insensitive search
    upper = clean.upper()
    for key, model in _NAME_TO_MODEL.items():
        if key.upper() == upper:
            return model
    # Substring match (e.g. "DATECS FP-2000" contains "FP-2000")
    for key, model in _NAME_TO_MODEL.items():
        if key.upper() in upper:
            return model
    return None


def _try_detect_transport(
    transport: BaseTransport,
    protocol_format: str,
    status_length: int,
    label: str = "",
) -> Optional[Dict[str, Any]]:
    """Core detection: send 0x5A via any transport, parse the response."""
    try:
        transport.open()
        frame = build_request(CMD_DIAGNOSTIC, data=None, seq=SEQ, protocol_format=protocol_format)
        log_info("DETECT_TRY", {
            "label": label, "protocol": protocol_format, "frame_hex": frame.hex(),
        })
        transport.write(frame)
        response = read_response(
            transport,
            timeout_s=DETECT_TIMEOUT_S,
            protocol_format=protocol_format,
            status_length=status_length,
        )
        log_info("DETECT_RESPONSE", {
            "label": label, "protocol": protocol_format,
            "fields": response.fields, "data_hex": response.data.hex(),
        })

        name = ""
        firmware = ""
        serial_number = ""
        fiscal_memory_number = ""

        raw = response.fields[0] if response.fields else ""
        parts = raw.split(",")
        if len(parts) >= 1:
            name = parts[0].strip()
        if len(parts) >= 2:
            firmware = parts[1].strip()
        if len(parts) >= 5:
            serial_number = parts[4].strip()
        if len(parts) >= 6:
            fiscal_memory_number = parts[5].strip()

        if not name:
            return None

        model = _match_model(name)
        return {
            "detected": True,
            "name": name,
            "model": model,
            "firmware": firmware,
            "serial_number": serial_number,
            "fiscal_memory_number": fiscal_memory_number,
            "protocol": protocol_format,
        }
    except DatecsProtocolError as exc:
        log_info("DETECT_PROTOCOL_FAIL", {
            "label": label, "protocol": protocol_format, "error": str(exc)[:120],
        })
        return None
    finally:
        try:
            transport.close()
        except Exception:
            pass


def _try_detect(
    port: str,
    baudrate: int,
    protocol_format: str,
    status_length: int,
) -> Optional[Dict[str, Any]]:
    """Try to detect a printer on a serial port."""
    config = SerialConfig(
        port=port, baudrate=baudrate, timeout_ms=int(DETECT_TIMEOUT_S * 1000),
    )
    transport = SerialTransport(config)
    try:
        result = _try_detect_transport(
            transport, protocol_format, status_length,
            label=f"{port}@{baudrate}",
        )
        if result:
            result["port"] = port
            result["baudrate"] = baudrate
        return result
    except (OSError, serial_lib.SerialException) as exc:
        log_info("DETECT_PORT_FAIL", {
            "port": port, "baudrate": baudrate, "error": str(exc)[:120],
        })
        raise


def detect_printer_on_port(
    port: str,
    baudrate: Optional[int] = None,
) -> Dict[str, Any]:
    """Detect a Datecs printer on a given COM port.
    
    Tries multiple baudrates and both protocol formats.
    Returns detection result or { detected: False }.
    """
    baudrates = [baudrate] if baudrate else COMMON_BAUDRATES

    # ── Try DatecsPay pinpad first (single fast PING packet) ──
    pinpad_result = _try_detect_pinpad(port, baudrates)
    if pinpad_result:
        return pinpad_result

    # ── Then try Datecs fiscal protocol (slower, multi-format) ──
    for baud in baudrates:
        for proto, slen in [("hex4", 8), ("byte", 6)]:
            try:
                result = _try_detect(port, baud, proto, slen)
                if result:
                    log_info("PRINTER_DETECTED", {
                        "port": port,
                        "baudrate": baud,
                        "protocol": proto,
                        "name": result["name"],
                        "model": result.get("model"),
                    })
                    return result
            except (OSError, serial_lib.SerialException) as exc:
                log_error("DETECT_SERIAL_ERROR", {
                    "port": port, "error": str(exc)[:120],
                })
                return {
                    "detected": False,
                    "port": port,
                    "error": str(exc),
                }
            except Exception as exc:
                log_error("DETECT_ERROR", {
                    "port": port, "baudrate": baud,
                    "protocol": proto, "error": str(exc)[:120],
                })
                continue

    return {"detected": False, "port": port, "error": "No Datecs printer found"}


def _try_detect_pinpad(
    port: str,
    baudrates: list[int],
) -> Optional[Dict[str, Any]]:
    """Try to detect a DatecsPay card reader (pinpad) on a serial port.

    Sends a PING command using the DatecsPay protocol. If it responds,
    follows up with GET PINPAD INFO to identify the device.
    """
    from app.datecspay_protocol import (
        CMD_BORICA, BorCmd, START_BYTE,
        build_packet, parse_response_packet,
        PinpadError, PinpadTimeoutError,
    )

    # Pinpad standard baud is 115200 — try it first
    pinpad_bauds = sorted(baudrates, key=lambda b: (0 if b == 115200 else 1, b))

    for baud in pinpad_bauds:
        config = SerialConfig(
            port=port, baudrate=baud, timeout_ms=1000,
        )
        transport = SerialTransport(config)
        try:
            transport.open()
            # Send PING
            ping_data = bytes([BorCmd.PING])
            packet = build_packet(CMD_BORICA, ping_data)
            log_info("DETECT_PINPAD_TRY", {"port": port, "baudrate": baud})
            transport.write(packet)

            # Read response
            import time
            buffer = bytearray()
            deadline = time.monotonic() + 1.0
            while time.monotonic() < deadline:
                chunk = transport.read(1)
                if chunk:
                    buffer.extend(chunk)
                    if len(buffer) >= 5 and buffer[0] == START_BYTE:
                        lh, ll = buffer[3], buffer[4]
                        total = 5 + ((lh << 8) | ll) + 1
                        if len(buffer) >= total:
                            break
                else:
                    time.sleep(0.005)

            if not buffer or buffer[0] != START_BYTE:
                continue

            resp = parse_response_packet(bytes(buffer))
            if resp.status != 0x00:
                continue

            # PING ok — now GET PINPAD INFO
            info_data = bytes([BorCmd.GET_PINPAD_INFO])
            info_packet = build_packet(CMD_BORICA, info_data)
            transport.write(info_packet)

            buffer2 = bytearray()
            deadline2 = time.monotonic() + 2.0
            while time.monotonic() < deadline2:
                chunk = transport.read(1)
                if chunk:
                    buffer2.extend(chunk)
                    if len(buffer2) >= 5 and buffer2[0] == START_BYTE:
                        lh2, ll2 = buffer2[3], buffer2[4]
                        total2 = 5 + ((lh2 << 8) | ll2) + 1
                        if len(buffer2) >= total2:
                            break
                else:
                    time.sleep(0.005)

            name = "DatecsPay PinPad"
            serial_number = ""
            firmware = ""
            terminal_id = ""

            if buffer2 and buffer2[0] == START_BYTE:
                try:
                    info_resp = parse_response_packet(bytes(buffer2))
                    if info_resp.status == 0x00 and len(info_resp.data) >= 34:
                        d = info_resp.data
                        name = d[0:20].decode("ascii", errors="replace").rstrip("\x00").strip()
                        serial_number = d[20:30].decode("ascii", errors="replace").rstrip("\x00").strip()
                        sv = d[30:34]
                        firmware = f"{sv[0]}.{sv[1]}.{sv[2]}.{sv[3]}"
                        if len(d) >= 42:
                            terminal_id = d[34:42].decode("ascii", errors="replace").rstrip("\x00").strip()
                except Exception:
                    pass

            log_info("PINPAD_DETECTED", {
                "port": port, "baudrate": baud,
                "name": name, "serial_number": serial_number,
                "firmware": firmware, "terminal_id": terminal_id,
            })
            return {
                "detected": True,
                "device_type": "pinpad",
                "name": name,
                "model": "datecspay_bluepad",
                "firmware": firmware,
                "serial_number": serial_number,
                "terminal_id": terminal_id,
                "port": port,
                "baudrate": baud,
                "protocol": "datecspay",
            }

        except (OSError, serial_lib.SerialException) as exc:
            log_info("DETECT_PINPAD_PORT_FAIL", {
                "port": port, "baudrate": baud, "error": str(exc)[:120],
            })
            return None  # port is busy / inaccessible — stop trying
        except Exception as exc:
            log_info("DETECT_PINPAD_FAIL", {
                "port": port, "baudrate": baud, "error": str(exc)[:120],
            })
            continue
        finally:
            try:
                transport.close()
            except Exception:
                pass

    return None


def detect_printer_on_lan(
    ip_address: str,
    tcp_port: int = 4999,
) -> Dict[str, Any]:
    """Detect a Datecs printer over LAN (TCP).

    Tries both protocol formats (hex4 for FP-700 series, byte for FP-2000 series).
    Returns detection result or { detected: False }.
    """
    label = f"{ip_address}:{tcp_port}"
    for proto, slen in [("hex4", 8), ("byte", 6)]:
        config = TcpConfig(
            ip_address=ip_address,
            tcp_port=tcp_port,
            timeout_ms=int(DETECT_TIMEOUT_S * 1000),
        )
        transport = TcpTransport(config)
        try:
            result = _try_detect_transport(
                transport, proto, slen, label=label,
            )
            if result:
                result["ip_address"] = ip_address
                result["tcp_port"] = tcp_port
                log_info("PRINTER_DETECTED_LAN", {
                    "ip_address": ip_address,
                    "tcp_port": tcp_port,
                    "protocol": proto,
                    "name": result["name"],
                    "model": result.get("model"),
                })
                return result
        except OSError as exc:
            log_error("DETECT_LAN_ERROR", {
                "ip_address": ip_address, "tcp_port": tcp_port, "error": str(exc)[:120],
            })
            return {
                "detected": False,
                "ip_address": ip_address,
                "tcp_port": tcp_port,
                "error": str(exc),
            }
        except Exception as exc:
            log_error("DETECT_LAN_ERROR", {
                "ip_address": ip_address, "tcp_port": tcp_port,
                "protocol": proto, "error": str(exc)[:120],
            })
            continue

    return {
        "detected": False,
        "ip_address": ip_address,
        "tcp_port": tcp_port,
        "error": "No Datecs printer found at this address",
    }
