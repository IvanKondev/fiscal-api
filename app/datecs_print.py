from __future__ import annotations

from app.adapters.datecs_base import DatecsBaseAdapter
from app.app_logging import log_info
from app.datecs_protocol import DatecsProtocolError, next_seq, send_command
from app.transports.factory import create_transport

CMD_OPEN_NONFISCAL = 0x26
CMD_CLOSE_NONFISCAL = 0x27
CMD_PRINT_TEXT = 0x2A
CMD_PAPER_CUT = 0x2E


class DatecsPrintError(DatecsProtocolError):
    pass


def _error_code(fields: list[str]) -> int | None:
    if not fields:
        return None
    try:
        return int(fields[0])
    except (ValueError, TypeError):  # noqa: PERF203
        return None


def _raise_on_error(fields: list[str], context: str, status: bytes | None = None) -> None:
    error_code = _error_code(fields)
    if error_code is None:
        return
    if error_code != 0:
        status_hex = status.hex() if status else ""
        raise DatecsPrintError(f"Datecs error {error_code} during {context} (status={status_hex})")


def _split_line(line: str, width: int) -> list[str]:
    if width <= 0:
        return [line]
    return [line[i : i + width] for i in range(0, len(line), width)] or [""]


def print_datecs_payload(
    printer: dict,
    adapter: DatecsBaseAdapter,
    payload_type: str,
    payload: dict,
    dry_run: bool = False,
) -> dict | None:
    timeout_ms = int(printer.get("timeout_ms", 5000))
    if dry_run:
        lines = adapter.build_lines(payload_type, payload)
        log_info(
            "DRY_RUN_DATECS_PRINT",
            {"printer_id": printer.get("id"), "lines": lines},
        )
        return None

    transport = create_transport(printer)
    seq = 0x20
    timeout_s = timeout_ms / 1000
    width = int(adapter.config.get("line_width") or 42)
    encoding = str(adapter.config.get("encoding") or adapter.default_encoding)
    cut_after = bool(adapter.config.get("cut_after", False))
    protocol_format = getattr(adapter, "protocol_format", "hex4")
    status_length = int(getattr(adapter, "status_length", 8) or 8)

    transport.open()
    try:
        response = send_command(
            transport,
            cmd=CMD_OPEN_NONFISCAL,
            seq=seq,
            timeout_s=timeout_s,
            protocol_format=protocol_format,
            status_length=status_length,
        )
        _raise_on_error(response.fields, "open non-fiscal receipt", response.status)
        seq = next_seq(seq)

        for line in adapter.build_lines(payload_type, payload):
            for chunk in _split_line(str(line), width):
                data = adapter.data_builder.nonfiscal_text(chunk).encode(encoding, errors="ignore")
                response = send_command(
                    transport,
                    cmd=CMD_PRINT_TEXT,
                    data=data,
                    seq=seq,
                    timeout_s=timeout_s,
                    protocol_format=protocol_format,
                    status_length=status_length,
                )
                _raise_on_error(response.fields, "print text", response.status)
                seq = next_seq(seq)

        close_response = send_command(
            transport,
            cmd=CMD_CLOSE_NONFISCAL,
            seq=seq,
            timeout_s=timeout_s,
            protocol_format=protocol_format,
            status_length=status_length,
        )
        _raise_on_error(close_response.fields, "close non-fiscal receipt", close_response.status)
        seq = next_seq(seq)

        # Extract receipt number from close response
        receipt_number = None
        if protocol_format == "hex4":
            # FP-700 series: fields = [ErrorCode, SlipNumber]
            if len(close_response.fields) >= 2 and close_response.fields[1].strip():
                receipt_number = close_response.fields[1].strip()
        else:
            # FP-2000 series: fields = [Allreceipt]
            if close_response.fields and close_response.fields[0].strip():
                receipt_number = close_response.fields[0].strip()

        if cut_after:
            response = send_command(
                transport,
                cmd=CMD_PAPER_CUT,
                seq=seq,
                timeout_s=timeout_s,
                protocol_format=protocol_format,
                status_length=status_length,
            )
            _raise_on_error(response.fields, "paper cut", response.status)

        return {
            "receipt_number": receipt_number,
            "payload_type": payload_type,
        }
    finally:
        transport.close()
