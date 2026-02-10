from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.adapters.datecs_base import DatecsBaseAdapter
from app.app_logging import log_error, log_info, log_warning
from app.datecs_protocol import DatecsProtocolError, DatecsResponse, next_seq, send_command
from app.transports import BaseTransport
from app.transports.factory import create_transport

CMD_OPEN_FISCAL = 0x30
CMD_SELL_ITEM = 0x31
CMD_PAYMENT = 0x35
CMD_CLOSE_FISCAL = 0x38
CMD_STORNO = 0x2E
CMD_REPORT = 0x45
CMD_REPORT_PLU = 0x6C
CMD_REPORT_DEPT = 0x75
CMD_REPORT_DEPT_PLU = 0x76
CMD_CASH = 0x46
CMD_OPERATOR_INFO = 0x70
CMD_STATUS = 0x4A
CMD_TRANSACTION_STATUS = 0x4C
CMD_CANCEL_RECEIPT = 0x3C
CMD_LAST_ERROR = 0x20
CMD_SET_DATE_TIME = 0x3D
CMD_READ_DATE_TIME = 0x3E
CMD_NRA_DATA = 0x25
CMD_SET_OPERATOR_NAME = 0x66

DATECS_ERROR_DETAILS = {
    -111018: "ERR_R_PAY_STARTED - Registration mode error: Payment is initiated.",
    -112001: "ERR_FP_SYNTAX_PARAM_1 - Invalid syntax of parameter 1.",
    -112101: "ERR_FP_SYNTAX_PARAM_1 - Invalid syntax of parameter 1.",
    -112107: "ERR_FP_SYNTAX_PARAM_7 - Invalid syntax of parameter 7.",
}

ERROR_TRANSLATIONS_BG = {
    "no_paper": "Няма хартия в принтера",
    "low_paper": "Хартията в принтера свършва",
    "cover_open": "Капакът на принтера е отворен",
    "printing_unit_fault": "Повреда в печатащото устройство",
    "general_error": "Обща грешка на принтера",
    "fiscal_memory_full": "Фискалната памет е пълна",
    "fiscal_memory_low": "Фискалната памет е почти пълна",
    "fiscal_memory_store_error": "Грешка при запис във фискална памет",
    "fiscal_memory_read_error": "Грешка при четене от фискална памет",
    "clock_not_set": "Часовникът не е настроен",
    "invalid_command_code": "Невалиден код на команда",
    "syntax_error": "Синтактична грешка",
    "command_not_allowed": "Командата не е разрешена в текущия режим",
    "amount_overflow": "Препълване на сума",
    "ram_reset": "RAM паметта е била изчистена",
    "low_battery": "Слаба батерия",
    "fiscal_receipt_open": "Вече има отворен фискален бон",
    "service_receipt_open": "Вече има отворен служебен бон",
    "storno_receipt_open": "Вече има отворена сторно бележка",
    "tax_terminal_not_responding": "Данъчният терминал не отговаря",
    "ej_near_end": "КЛЕН приключва",
    "ej_end": "КЛЕН е пълен",
    "head_overheated": "Печатащата глава е прегряла",
    "uic_missing": "ЕИК не е въведен",
    "unique_id_missing": "Уникален номер не е въведен",
}

_SEQ_BY_PRINTER: dict[int, int] = {}


class DatecsFiscalError(DatecsProtocolError):
    def __init__(self, message: str, code: int | None = None, context: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.context = context


def _encoding(adapter: DatecsBaseAdapter) -> str:
    return str(adapter.config.get("encoding") or adapter.default_encoding)


def _operator_data(
    payload: Dict[str, Any],
    printer: Dict[str, Any],
    require_till: bool = True,
) -> str:
    operator = payload.get("operator") or printer.get("config", {}).get("operator") or {}
    op_num = (
        payload.get("operator_id")
        or operator.get("id")
        or operator.get("op_num")
        or operator.get("number")
    )
    password = payload.get("operator_password") or operator.get("password")
    till = (
        payload.get("operator_till")
        or operator.get("till")
        or operator.get("till_num")
        or operator.get("till_number")
    )
    if not (op_num or password or till):
        return ""
    op_num = str(op_num).strip() if op_num is not None else ""
    password = str(password).strip() if password is not None else ""
    till = str(till).strip() if till is not None else ""

    def _normalize_numeric(value: str) -> str:
        if value and value.isdigit():
            return str(int(value))
        return value

    op_num = _normalize_numeric(op_num)
    till = _normalize_numeric(till)
    if op_num == "0":
        op_num = ""
    if till == "0":
        till = ""
    if require_till:
        if not (op_num and password and till):
            raise ValueError("Operator info requires id, password, till.")
        return f"{op_num}\t{password}\t{till}\t"
    if not (op_num and password):
        raise ValueError("Operator info requires id and password.")
    if till:
        return f"{op_num}\t{password}\t{till}\t"
    return f"{op_num}\t{password}\t"


def _encode_data(adapter: DatecsBaseAdapter, data: str) -> bytes:
    if not data:
        return b""
    return data.encode(_encoding(adapter), errors="ignore")


def _error_code(fields: list[str]) -> Optional[int]:
    if not fields:
        return None
    try:
        value = int(fields[0])
    except (ValueError, TypeError):  # noqa: PERF203
        return None
    return value if value < 0 else None


def _translate_error_flags(flags: Dict[str, bool]) -> str:
    """Translate printer error flags to Bulgarian user-friendly messages."""
    messages = []
    for flag, value in flags.items():
        if value and flag in ERROR_TRANSLATIONS_BG:
            messages.append(ERROR_TRANSLATIONS_BG[flag])
    return "; ".join(messages) if messages else ""


def _decode_status_flags(status: bytes | None) -> Dict[str, bool]:
    if not status:
        return {}
    flags: Dict[str, bool] = {}

    def _set_flag(byte_index: int, bit_index: int, name: str) -> None:
        if len(status) > byte_index and (status[byte_index] & (1 << bit_index)):
            flags[name] = True

    # Byte 0
    _set_flag(0, 6, "cover_open")
    _set_flag(0, 5, "general_error")
    _set_flag(0, 4, "printing_unit_fault")
    _set_flag(0, 3, "no_customer_display")
    _set_flag(0, 2, "clock_not_set")
    _set_flag(0, 1, "invalid_command_code")
    _set_flag(0, 0, "syntax_error")
    # Byte 1
    _set_flag(1, 6, "tax_terminal_not_responding")
    _set_flag(1, 5, "service_receipt_rotated_open")
    _set_flag(1, 4, "storno_receipt_open")
    _set_flag(1, 3, "low_battery")
    _set_flag(1, 2, "ram_reset")
    _set_flag(1, 1, "command_not_allowed")
    _set_flag(1, 0, "amount_overflow")
    # Byte 2
    _set_flag(2, 6, "ej_near_end")
    _set_flag(2, 5, "service_receipt_open")
    _set_flag(2, 4, "ej_near")
    _set_flag(2, 3, "fiscal_receipt_open")
    _set_flag(2, 2, "ej_end")
    _set_flag(2, 1, "low_paper")
    _set_flag(2, 0, "no_paper")
    # Byte 4
    _set_flag(4, 6, "head_overheated")
    _set_flag(4, 5, "fiscal_error_or")
    _set_flag(4, 4, "fiscal_memory_full")
    _set_flag(4, 3, "fiscal_memory_low")
    if len(status) > 4:
        if not (status[4] & (1 << 1)):
            flags["uic_missing"] = True
        if not (status[4] & (1 << 2)):
            flags["unique_id_missing"] = True
        if status[4] & (1 << 1):
            flags["uic_set"] = True
    _set_flag(4, 0, "fiscal_memory_store_error")
    # Byte 5
    _set_flag(5, 5, "fiscal_memory_read_error")
    _set_flag(5, 4, "tax_rates_set")
    _set_flag(5, 3, "fiscal_mode")
    _set_flag(5, 2, "last_store_failed")
    _set_flag(5, 1, "fiscal_memory_formatted")
    _set_flag(5, 0, "fiscal_memory_readonly")

    return flags


def _raise_on_error(
    fields: list[str],
    context: str,
    status: bytes | None = None,
    data: str | None = None,
    correlation_id: str | None = None,
) -> None:
    error_code = _error_code(fields)
    if error_code is None:
        return
    status_hex = status.hex() if status else ""
    status_flags = _decode_status_flags(status)
    description = DATECS_ERROR_DETAILS.get(error_code, "Unknown Datecs error.")
    hint = ""
    suspect = ""
    if error_code == -111018:
        hint = "Плащането е започнато, но не е приключено. Добави плащане за остатъка."
        if not suspect and data:
            suspect = "Плащането е по-малко от тотала и има остатък за плащане."
    elif error_code in {-112001, -112101}:
        if context == "open receipt":
            hint = (
                "Провери оператор (ID/парола/каса), HEADER>=2 реда, UIC/часовник,"
                " и дали вече няма отворен фискален бон."
            )
            if not suspect:
                if status_flags.get("fiscal_receipt_open") or status_flags.get(
                    "service_receipt_open"
                ):
                    suspect = "Има вече отворен фискален/сервизен бон."
                elif status_flags.get("clock_not_set"):
                    suspect = "Часовникът не е настроен."
                elif status_flags.get("uic_missing"):
                    suspect = "UIC не е зададен."
                elif status_flags.get("command_not_allowed"):
                    suspect = "Командата не е позволена в текущия режим."
                elif status_flags.get("fiscal_memory_full") or status_flags.get("ej_end"):
                    suspect = "Фискалната памет/ЕЖ е пълна или блокирана."
            if data:
                normalized = data.strip()
                if normalized.startswith("48\t"):
                    suspect = "DATA започва с '48\\t' (cmd е в DATA вместо само параметрите)."
                elif "\t" not in normalized:
                    suspect = "DATA няма TAB разделители (очаквано е OpNum<TAB>Password<TAB>Till)."
                else:
                    parts = [part.strip() for part in normalized.split("\t") if part != ""]
                    if parts:
                        op_num = parts[0]
                        password = parts[1] if len(parts) > 1 else ""
                        till = parts[2] if len(parts) > 2 else ""
                        if not op_num or not op_num.isdigit():
                            suspect = "OpNum не е число или има скрит символ."
                        elif not (1 <= int(op_num) <= 30):
                            suspect = "OpNum трябва да е между 1 и 30 (провери оператори)."
                        elif password and (not password.isdigit() or not (1 <= len(password) <= 8)):
                            suspect = "Паролата трябва да е 1-8 цифри според конфигурацията."
                        elif till and (not till.isdigit() or int(till) < 1):
                            suspect = "Till (каса) трябва да е число >= 1."
        if context == "open receipt" and not suspect:
            suspect = (
                "Параметрите изглеждат валидни; вероятно операторът/паролата не са активни"
                " или устройството очаква празни параметри."
            )
        elif context == "report":
            hint = "Параметър 1 (option) трябва да е 0/2, по желание N, или ?/* според модела."
        else:
            hint = "Провери параметрите на командата и режима на принтера."
    log_error(
        "DATECS_ERROR",
        {
            "context": context,
            "code": error_code,
            "description": description,
            "hint": hint,
            "suspect": suspect,
            "status_hex": status_hex,
            "status_flags": status_flags,
            "fields": fields,
            "data": data,
            "correlation_id": correlation_id,
        },
    )
    
    user_friendly_errors = _translate_error_flags(status_flags)
    parts = [part for part in [user_friendly_errors, hint, suspect] if part]
    hint_text = f" ({'; '.join(parts)})" if parts else ""
    
    raise DatecsFiscalError(
        f"Грешка от принтера {error_code}: {description}{hint_text}",
        code=error_code,
        context=context,
    )


def _send(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    cmd: int,
    data: str,
    seq: int,
    timeout_s: float,
    context: str,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    next_value, _ = _send_with_response(
        transport,
        adapter,
        cmd,
        data,
        seq,
        timeout_s,
        context,
        printer_id,
        correlation_id=correlation_id,
    )
    return next_value


def _send_with_response(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    cmd: int,
    data: str,
    seq: int,
    timeout_s: float,
    context: str,
    printer_id: int,
    correlation_id: str | None = None,
    skip_raise: bool = False,
):
    payload = _encode_data(adapter, data)
    protocol_format = getattr(adapter, "protocol_format", "hex4")
    status_length = int(getattr(adapter, "status_length", 8) or 8)
    if context in {
        "report",
        "cash",
        "open receipt",
        "status",
        "transaction status",
        "cancel receipt",
        "read datetime",
        "set datetime",
        "last error",
        "sell item",
        "payment",
        "close receipt",
        "storno open",
        "storno item",
        "storno payment",
        "storno close",
        "nra data",
        "set operator name",
    }:
        log_info(
            "DATECS_SEND",
            {
                "context": context,
                "cmd": f"0x{cmd:02X}",
                "seq": seq,
                "encoding": _encoding(adapter),
                "data": data,
                "data_repr": repr(data),
                "data_len": len(payload),
                "data_hex": payload.hex(),
                "correlation_id": correlation_id,
            },
        )
    response = send_command(
        transport,
        cmd=cmd,
        data=payload,
        seq=seq,
        timeout_s=timeout_s,
        protocol_format=protocol_format,
        status_length=status_length,
    )
    next_value = next_seq(seq)
    try:
        if not skip_raise:
            _raise_on_error(response.fields, context, response.status, data, correlation_id)
    finally:
        _SEQ_BY_PRINTER[printer_id] = next_value
    return next_value, response


def _ensure_payment_completed(
    response: DatecsResponse,
    context: str,
    correlation_id: str | None = None,
) -> None:
    if not response.fields:
        return
    status = response.fields[1] if len(response.fields) > 1 else ""
    remainder = response.fields[2] if len(response.fields) > 2 else ""
    if status == "D":
        try:
            remainder_float = float(remainder.replace(",", ".")) if remainder else 0.0
        except (ValueError, AttributeError):
            remainder_float = 0.0
        
        if remainder_float > 0.02:
            hint = f"Остатък за плащане: {remainder}."
            log_warning(
                "DATECS_PAYMENT_INCOMPLETE",
                {
                    "context": context,
                    "status": status,
                    "remainder": remainder,
                    "correlation_id": correlation_id,
                },
            )
            raise DatecsFiscalError(
                f"Payment incomplete. {hint}",
                context=context,
            )


def _diagnostic_status(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    try:
        seq, response = _send_with_response(
            transport,
            adapter,
            CMD_STATUS,
            adapter.data_builder.status_data(),
            seq,
            timeout_s,
            "status",
            printer_id,
            correlation_id=correlation_id,
        )
        log_info(
            "DATECS_STATUS_SUCCESS",
            {
                "printer_id": printer_id,
                "status_hex": response.status.hex(),
                "status_flags": _decode_status_flags(response.status),
                "fields": response.fields,
                "correlation_id": correlation_id,
            },
        )
    except DatecsFiscalError as exc:
        log_error(
            "DATECS_STATUS_FAILED",
            {
                "printer_id": printer_id,
                "error_code": exc.code,
                "error_msg": str(exc),
                "hint": "Не може да извлече статус байтове.",
                "correlation_id": correlation_id,
            },
        )
    except Exception as exc:
        log_error(
            "DATECS_STATUS_EXCEPTION",
            {"printer_id": printer_id, "error": str(exc), "correlation_id": correlation_id},
        )
    return seq


def _read_last_error(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> tuple[int, list[str]]:
    try:
        seq, response = _send_with_response(
            transport,
            adapter,
            CMD_LAST_ERROR,
            "",
            seq,
            timeout_s,
            "last error",
            printer_id,
            correlation_id=correlation_id,
            skip_raise=True,
        )
        return seq, response.fields
    except Exception as exc:
        log_warning(
            "DATECS_LAST_ERROR_FAILED",
            {"printer_id": printer_id, "error": str(exc), "correlation_id": correlation_id},
        )
        return seq, []


def _format_last_error(fields: list[str]) -> str:
    if not fields:
        return ""
    if len(fields) >= 4:
        cmd, code, when, text = fields[:4]
        parts = [part for part in [f"cmd {cmd}" if cmd else "", f"код {code}" if code else "", when, text] if part]
        return "Последна грешка: " + ", ".join(parts)
    return "Последна грешка: " + ", ".join(fields)


def _format_printer_datetime(value: datetime) -> str:
    return value.strftime("%d-%m-%y %H:%M:%S")


def _parse_printer_datetime(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    for fmt in (
        "%d-%m-%y %H:%M:%S",
        "%d-%m-%y %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _read_printer_datetime(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> tuple[int, str, datetime | None]:
    seq, response = _send_with_response(
        transport,
        adapter,
        CMD_READ_DATE_TIME,
        "",
        seq,
        timeout_s,
        "read datetime",
        printer_id,
        correlation_id=correlation_id,
    )
    protocol_format = getattr(adapter, "protocol_format", "hex4")
    if protocol_format == "hex4":
        # FP-700 series: fields = [ErrorCode, DateTime]
        raw = response.fields[1].strip() if len(response.fields) >= 2 else ""
    else:
        # FP-2000 series: fields = [DateTime]
        raw = response.fields[0].strip() if response.fields else ""
    # Strip trailing "DST" marker if present
    if raw.endswith(" DST"):
        raw = raw[:-4].strip()
    parsed = _parse_printer_datetime(raw) if raw else None
    return seq, raw, parsed


def _set_printer_datetime(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    value: datetime,
    correlation_id: str | None = None,
) -> int:
    data = _format_printer_datetime(value)
    return _send(
        transport,
        adapter,
        CMD_SET_DATE_TIME,
        data,
        seq,
        timeout_s,
        "set datetime",
        printer_id,
        correlation_id=correlation_id,
    )


def _diagnostic_operator_info(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    op_num: str,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    try:
        seq = _send(
            transport,
            adapter,
            CMD_OPERATOR_INFO,
            f"{op_num}\t",
            seq,
            timeout_s,
            "operator info",
            printer_id,
            correlation_id=correlation_id,
        )
        log_info(
            "DATECS_OPERATOR_INFO_SUCCESS",
            {
                "printer_id": printer_id,
                "op_num": op_num,
                "message": "70h operator info retrieved.",
                "correlation_id": correlation_id,
            },
        )
    except DatecsFiscalError as exc:
        log_error(
            "DATECS_OPERATOR_INFO_FAILED",
            {
                "printer_id": printer_id,
                "op_num": op_num,
                "error_code": exc.code,
                "error_msg": str(exc),
                "hint": "Оператор не е активен или няма права.",
                "correlation_id": correlation_id,
            },
        )
    except Exception as exc:
        log_error(
            "DATECS_OPERATOR_INFO_EXCEPTION",
            {
                "printer_id": printer_id,
                "op_num": op_num,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )
    return seq


def _transaction_status_snapshot(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    try:
        seq, response = _send_with_response(
            transport,
            adapter,
            CMD_TRANSACTION_STATUS,
            "",
            seq,
            timeout_s,
            "transaction status",
            printer_id,
            correlation_id=correlation_id,
        )
        log_info(
            "DATECS_TRANSACTION_STATUS",
            {
                "printer_id": printer_id,
                "fields": response.fields,
                "status_hex": response.status.hex(),
                "status_flags": _decode_status_flags(response.status),
                "correlation_id": correlation_id,
            },
        )
    except DatecsFiscalError as exc:
        log_error(
            "DATECS_TRANSACTION_STATUS_FAILED",
            {
                "printer_id": printer_id,
                "error_code": exc.code,
                "error_msg": str(exc),
                "correlation_id": correlation_id,
            },
        )
    except Exception as exc:
        log_error(
            "DATECS_TRANSACTION_STATUS_EXCEPTION",
            {"printer_id": printer_id, "error": str(exc), "correlation_id": correlation_id},
        )
    return seq


def _cancel_receipt(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    log_warning(
        "DATECS_CANCEL_RECEIPT",
        {"printer_id": printer_id, "message": "Attempting cancel receipt", "correlation_id": correlation_id},
    )
    return _send(
        transport,
        adapter,
        CMD_CANCEL_RECEIPT,
        "",
        seq,
        timeout_s,
        "cancel receipt",
        printer_id,
        correlation_id=correlation_id,
    )


def _preflight_cleanup(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    seq, response = _send_with_response(
        transport,
        adapter,
        CMD_STATUS,
        adapter.data_builder.status_data(),
        seq,
        timeout_s,
        "status",
        printer_id,
        correlation_id=correlation_id,
    )
    status_flags = _decode_status_flags(response.status)
    log_info(
        "DATECS_STATUS_SNAPSHOT",
        {
            "printer_id": printer_id,
            "status_hex": response.status.hex(),
            "status_flags": status_flags,
            "fields": response.fields,
            "correlation_id": correlation_id,
        },
    )

    # Block early if printer has a hardware problem
    hw_errors = []
    if status_flags.get("cover_open"):
        hw_errors.append("Капакът на принтера е отворен")
    if status_flags.get("no_paper"):
        hw_errors.append("Няма хартия в принтера")
    if status_flags.get("printing_unit_fault"):
        hw_errors.append("Повреда в печатащото устройство")
    if hw_errors:
        raise DatecsFiscalError(
            f"Принтерът не е готов: {'; '.join(hw_errors)}",
            context="preflight",
        )

    seq = _transaction_status_snapshot(
        transport,
        adapter,
        seq,
        timeout_s,
        printer_id,
        correlation_id=correlation_id,
    )
    if status_flags.get("fiscal_receipt_open") or status_flags.get("service_receipt_open") or status_flags.get(
        "storno_receipt_open"
    ):
        seq = _cancel_receipt(
            transport,
            adapter,
            seq,
            timeout_s,
            printer_id,
            correlation_id=correlation_id,
        )
        seq = _diagnostic_status(
            transport,
            adapter,
            seq,
            timeout_s,
            printer_id,
            correlation_id=correlation_id,
        )
    return seq


def _set_operator_name(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    op_num: str,
    name: str,
    password: str,
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    """Program operator name on printer (Datecs CMD 0x66).
    Data format: <OpNum>\t<Name>\t<Password>\t
    """
    data = f"{op_num}\t{name}\t{password}\t"
    try:
        seq = _send(
            transport,
            adapter,
            CMD_SET_OPERATOR_NAME,
            data,
            seq,
            timeout_s,
            "set operator name",
            printer_id,
            correlation_id=correlation_id,
        )
        log_info(
            "DATECS_SET_OPERATOR_NAME",
            {
                "printer_id": printer_id,
                "op_num": op_num,
                "name": name,
                "correlation_id": correlation_id,
            },
        )
    except DatecsFiscalError as exc:
        log_warning(
            "DATECS_SET_OPERATOR_NAME_FAILED",
            {
                "printer_id": printer_id,
                "op_num": op_num,
                "name": name,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )
    return seq


def _open_receipt_with_fallback(
    transport: BaseTransport,
    adapter: DatecsBaseAdapter,
    payload: Dict[str, Any],
    printer: Dict[str, Any],
    seq: int,
    timeout_s: float,
    printer_id: int,
    correlation_id: str | None = None,
) -> int:
    operator = payload.get("operator") or printer.get("config", {}).get("operator") or {}
    op_num = str(operator.get("id") or operator.get("op_num") or operator.get("number") or "").strip()
    
    log_info(
        "DATECS_DIAGNOSTICS_START",
        {
            "printer_id": printer_id,
            "op_num": op_num,
            "message": "Running diagnostics before open receipt.",
            "correlation_id": correlation_id,
        },
    )

    seq = _preflight_cleanup(
        transport,
        adapter,
        seq,
        timeout_s,
        printer_id,
        correlation_id=correlation_id,
    )

    # Extract operator fields early (needed for diagnostics + set name)
    password = str(
        payload.get("operator_password") or operator.get("password") or ""
    ).strip()
    till = str(
        payload.get("operator_till")
        or operator.get("till")
        or operator.get("till_num")
        or operator.get("till_number")
        or ""
    ).strip()

    if op_num:
        seq = _diagnostic_operator_info(
            transport,
            adapter,
            op_num,
            seq,
            timeout_s,
            printer_id,
            correlation_id=correlation_id,
        )

    # Set operator name (waiter name) if provided — Datecs CMD 0x66
    operator_name = (
        payload.get("operator_name")
        or operator.get("name")
        or ""
    )
    if operator_name and op_num:
        seq = _set_operator_name(
            transport,
            adapter,
            op_num,
            operator_name,
            password,
            seq,
            timeout_s,
            printer_id,
            correlation_id=correlation_id,
        )
    invoice = "I" if payload.get("invoice") else ""
    nsale = str(
        payload.get("nsale") or payload.get("n_sale")
        or payload.get("sale_id") or payload.get("unp")
        or payload.get("UNP") or ""
    ).strip()

    if not (op_num and password and till):
        raise ValueError("Operator info requires id, password, till.")

    builder = adapter.data_builder
    data = builder.open_receipt(op_num, password, till, invoice, nsale)

    log_info(
        "DATECS_OPEN_RECEIPT_DATA",
        {
            "printer_id": printer_id,
            "data": data,
            "data_repr": repr(data),
            "correlation_id": correlation_id,
        },
    )

    return _send(
        transport,
        adapter,
        CMD_OPEN_FISCAL,
        data,
        seq,
        timeout_s,
        "open receipt",
        printer_id,
        correlation_id=correlation_id,
    )


def _report_command(payload: Dict[str, Any]) -> int:
    raw = payload.get("command") or payload.get("cmd")
    if raw is None:
        return CMD_REPORT
    if isinstance(raw, int):
        return raw
    text = str(raw).strip().upper()
    mapping = {
        "45H": CMD_REPORT,
        "69": CMD_REPORT,
        "0X45": CMD_REPORT,
        "6CH": CMD_REPORT_PLU,
        "108": CMD_REPORT_PLU,
        "0X6C": CMD_REPORT_PLU,
        "75H": CMD_REPORT_DEPT,
        "117": CMD_REPORT_DEPT,
        "0X75": CMD_REPORT_DEPT,
        "76H": CMD_REPORT_DEPT_PLU,
        "118": CMD_REPORT_DEPT_PLU,
        "0X76": CMD_REPORT_DEPT_PLU,
    }
    if text in mapping:
        return mapping[text]
    if text.startswith("0X"):
        return int(text, 16)
    if text.endswith("H"):
        return int(text[:-1], 16)
    if all(ch in "0123456789ABCDEF" for ch in text):
        return int(text, 16)
    return int(text)


def _build_storno_data(payload: Dict[str, Any]) -> str:
    st_type = payload.get("storno_type", payload.get("type", 0))
    original = payload.get("original", {}) or {}
    doc_no = original.get("doc_no") or original.get("document") or ""
    date = original.get("date") or ""
    fm = original.get("fm") or ""
    unp = original.get("unp") or ""
    parts = [str(st_type)]
    if doc_no:
        parts.append(str(doc_no))
    if date:
        parts.append(str(date))
    if fm:
        parts.append(str(fm))
    if unp:
        parts.append(str(unp))
    return ",".join(parts)


def fiscal_operation(
    printer: Dict[str, Any],
    adapter: DatecsBaseAdapter,
    payload_type: str,
    payload: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    printer_id = int(printer.get("id") or 0)
    correlation_id = uuid4().hex
    timeout_ms = int(printer.get("timeout_ms", 5000))
    if dry_run:
        log_info(
            "DRY_RUN_DATECS_FISCAL",
            {
                "printer_id": printer.get("id"),
                "payload_type": payload_type,
                "payload": payload,
                "correlation_id": correlation_id,
            },
        )
        return {"dry_run": True, "correlation_id": correlation_id}

    transport = create_transport(printer)
    seq = _SEQ_BY_PRINTER.get(printer_id, 0x20)
    timeout_s = timeout_ms / 1000

    transport.open()
    try:
        log_info(
            "DATECS_FISCAL_JOB_START",
            {
                "printer_id": printer_id,
                "payload_type": payload_type,
                "correlation_id": correlation_id,
            },
        )
        if payload_type == "fiscal_receipt":
            seq = _open_receipt_with_fallback(
                transport,
                adapter,
                payload,
                printer,
                seq,
                timeout_s,
                printer_id,
                correlation_id=correlation_id,
            )
            for item in payload.get("items", []):
                seq = _send(
                    transport,
                    adapter,
                    CMD_SELL_ITEM,
                    adapter.data_builder.sale(item),
                    seq,
                    timeout_s,
                    "sell item",
                    printer_id,
                    correlation_id=correlation_id,
                )
            payments = payload.get("payments") or []
            if not payments:
                raise ValueError("At least one payment is required.")
            
            last_payment_response = None
            for payment in payments:
                seq, last_payment_response = _send_with_response(
                    transport,
                    adapter,
                    CMD_PAYMENT,
                    adapter.data_builder.payment(payment),
                    seq,
                    timeout_s,
                    "payment",
                    printer_id,
                    correlation_id=correlation_id,
                )
            
            if last_payment_response:
                _ensure_payment_completed(
                    last_payment_response,
                    "payment",
                    correlation_id=correlation_id,
                )
            seq, close_response = _send_with_response(
                transport,
                adapter,
                CMD_CLOSE_FISCAL,
                "",
                seq,
                timeout_s,
                "close receipt",
                printer_id,
                correlation_id=correlation_id,
            )
            
            log_info(
                "DATECS_CLOSE_RESPONSE",
                {
                    "printer_id": printer_id,
                    "fields": close_response.fields,
                    "fields_count": len(close_response.fields),
                    "data_hex": close_response.data.hex(),
                    "data_repr": repr(close_response.data),
                    "status_hex": close_response.status.hex(),
                    "correlation_id": correlation_id,
                },
            )
            
            seq = _diagnostic_status(
                transport,
                adapter,
                seq,
                timeout_s,
                printer_id,
                correlation_id=correlation_id,
            )
            _SEQ_BY_PRINTER[printer_id] = seq
            
            receipt_number = None
            protocol_fmt = getattr(adapter, "protocol_format", "hex4")
            if protocol_fmt == "hex4":
                # FP-700 series: fields = [ErrorCode, SlipNumber]
                if len(close_response.fields) >= 2 and close_response.fields[1].strip():
                    receipt_number = close_response.fields[1].strip()
            else:
                # FP-2000 series: close returns day-counts only.
                # Query NRA data (cmd 0x25, type "1") for global doc number.
                # Response: "P,DT,Closure,FiscRec,LastFiscal,LastDoc,Journal"
                try:
                    seq, nra_response = _send_with_response(
                        transport,
                        adapter,
                        CMD_NRA_DATA,
                        "1",
                        seq,
                        timeout_s,
                        "nra data",
                        printer_id,
                        correlation_id=correlation_id,
                        skip_raise=True,
                    )
                    log_info("DATECS_NRA_DATA_RESPONSE", {
                        "fields": nra_response.fields,
                        "fields_count": len(nra_response.fields),
                        "data_hex": nra_response.data.hex(),
                        "correlation_id": correlation_id,
                    })
                    # NRA type "1" response (may or may not have "P" prefix):
                    # [P,]DT,Closure,FiscRec,LastFiscal,LastDoc,Journal
                    # Parse from end: LastDoc = [-2], Journal = [-1]
                    all_parts = []
                    for f in nra_response.fields:
                        all_parts.extend(p.strip() for p in f.split(","))
                    if len(all_parts) >= 4:
                        receipt_number = all_parts[-2]  # LastDoc
                except Exception as exc:
                    log_info("DATECS_NRA_DATA_FAILED", {"error": str(exc), "correlation_id": correlation_id})
                    # Fallback to close response Allreceipt
                    if close_response.fields and close_response.fields[0].strip():
                        parts = close_response.fields[0].split(",")
                        receipt_number = parts[0].strip()
            if receipt_number == "0" or not receipt_number:
                receipt_number = None
            
            total_amount = sum(
                float(item.get("price", 0)) * float(item.get("quantity", 1))
                for item in payload.get("items", [])
            )
            
            payment_methods = []
            for payment in payments:
                payment_type = payment.get("type", "P")
                payment_amount = float(payment.get("amount", 0))
                payment_name = {
                    "P": "В брой",
                    "C": "Кредитна карта",
                    "N": "Дебитна карта",
                    "D": "Ваучер",
                    "I": "Банка",
                }.get(payment_type, payment_type)
                payment_methods.append({"type": payment_name, "amount": payment_amount})
            
            return {
                "receipt_number": receipt_number,
                "payload_type": "fiscal_receipt",
                "total_amount": round(total_amount, 2),
                "payment_methods": payment_methods,
                "correlation_id": correlation_id,
            }
        if payload_type == "storno":
            operator_data = _operator_data(payload, printer)
            storno_data = _build_storno_data(payload)
            data = f"{operator_data},{storno_data}" if operator_data else storno_data
            seq = _send(
                transport,
                adapter,
                CMD_STORNO,
                data,
                seq,
                timeout_s,
                "storno open",
                printer_id,
                correlation_id=correlation_id,
            )
            if payload.get("auto"):
                _SEQ_BY_PRINTER[printer_id] = seq
                return
            for item in payload.get("items", []):
                seq = _send(
                    transport,
                    adapter,
                    CMD_SELL_ITEM,
                    adapter.data_builder.sale(item),
                    seq,
                    timeout_s,
                    "storno item",
                    printer_id,
                    correlation_id=correlation_id,
                )
            payments = payload.get("payments") or []
            if not payments:
                raise ValueError("At least one payment is required.")
            
            last_payment_response = None
            for payment in payments:
                seq, last_payment_response = _send_with_response(
                    transport,
                    adapter,
                    CMD_PAYMENT,
                    adapter.data_builder.payment(payment),
                    seq,
                    timeout_s,
                    "storno payment",
                    printer_id,
                    correlation_id=correlation_id,
                )
            
            if last_payment_response:
                _ensure_payment_completed(
                    last_payment_response,
                    "storno payment",
                    correlation_id=correlation_id,
                )
            seq, close_response = _send_with_response(
                transport,
                adapter,
                CMD_CLOSE_FISCAL,
                "",
                seq,
                timeout_s,
                "storno close",
                printer_id,
                correlation_id=correlation_id,
            )
            
            log_info(
                "DATECS_CLOSE_RESPONSE",
                {
                    "printer_id": printer_id,
                    "fields": close_response.fields,
                    "status_hex": close_response.status.hex(),
                    "correlation_id": correlation_id,
                },
            )
            
            seq = _diagnostic_status(
                transport,
                adapter,
                seq,
                timeout_s,
                printer_id,
                correlation_id=correlation_id,
            )
            _SEQ_BY_PRINTER[printer_id] = seq
            
            receipt_number = None
            protocol_fmt = getattr(adapter, "protocol_format", "hex4")
            if protocol_fmt == "hex4":
                # FP-700 series: fields = [ErrorCode, SlipNumber]
                if len(close_response.fields) >= 2 and close_response.fields[1].strip():
                    receipt_number = close_response.fields[1].strip()
            else:
                # FP-2000 series: close returns day-counts only.
                # Query NRA data (cmd 0x25, type "1") for global doc number.
                try:
                    seq, nra_response = _send_with_response(
                        transport,
                        adapter,
                        CMD_NRA_DATA,
                        "1",
                        seq,
                        timeout_s,
                        "nra data",
                        printer_id,
                        correlation_id=correlation_id,
                        skip_raise=True,
                    )
                    all_parts = []
                    for f in nra_response.fields:
                        all_parts.extend(p.strip() for p in f.split(","))
                    if len(all_parts) >= 4:
                        receipt_number = all_parts[-2]  # LastDoc
                except Exception as exc:
                    log_info("DATECS_NRA_DATA_FAILED", {"error": str(exc), "correlation_id": correlation_id})
                    if close_response.fields and close_response.fields[0].strip():
                        parts = close_response.fields[0].split(",")
                        receipt_number = parts[0].strip()
            if receipt_number == "0" or not receipt_number:
                receipt_number = None
            
            total_amount = sum(
                float(item.get("price", 0)) * float(item.get("quantity", 1))
                for item in payload.get("items", [])
            )
            
            payment_methods = []
            for payment in payments:
                payment_type = payment.get("type", "P")
                payment_amount = float(payment.get("amount", 0))
                payment_name = {
                    "P": "В брой",
                    "C": "Кредитна карта",
                    "N": "Дебитна карта",
                    "D": "Ваучер",
                    "I": "Банка",
                }.get(payment_type, payment_type)
                payment_methods.append({"type": payment_name, "amount": payment_amount})
            
            return {
                "receipt_number": receipt_number,
                "payload_type": "storno",
                "total_amount": round(total_amount, 2),
                "payment_methods": payment_methods,
                "correlation_id": correlation_id,
            }
        if payload_type == "report":
            report_data = adapter.data_builder.report(payload)
            report_cmd = _report_command(payload)
            report_timeout = max(timeout_s, 30.0)
            seq, report_response = _send_with_response(
                transport,
                adapter,
                report_cmd,
                report_data,
                seq,
                report_timeout,
                "report",
                printer_id,
                correlation_id=correlation_id,
            )
            status_flags = _decode_status_flags(report_response.status)
            error_flags = {
                key
                for key in {
                    "command_not_allowed",
                    "syntax_error",
                    "invalid_command_code",
                    "no_paper",
                    "cover_open",
                    "fiscal_receipt_open",
                    "service_receipt_open",
                    "storno_receipt_open",
                    "clock_not_set",
                }
                if status_flags.get(key)
            }
            if status_flags.get("general_error") or error_flags:
                seq, last_error_fields = _read_last_error(
                    transport,
                    adapter,
                    seq,
                    timeout_s,
                    printer_id,
                    correlation_id=correlation_id,
                )
                _SEQ_BY_PRINTER[printer_id] = seq
                hint = _translate_error_flags(status_flags)
                last_error_text = _format_last_error(last_error_fields)
                parts = [part for part in [hint, last_error_text] if part]
                hint_text = f" ({'; '.join(parts)})" if parts else ""
                raise DatecsFiscalError(
                    f"Z отчетът е отказан от принтера.{hint_text}",
                    context="report",
                )
            _SEQ_BY_PRINTER[printer_id] = seq
            if report_response.fields and len(report_response.fields) == 1:
                error_code = report_response.fields[0].strip().upper()
                if error_code in {"T", "F"}:
                    hint = (
                        "Грешка при Z отчет (код T): проверете дата/час, регистрация в НАП, SIM карта "
                        "или връзка към NRA."
                    )
                    raise DatecsFiscalError(hint, context="report")
            return {
                "payload_type": "report",
                "report_type": payload.get("type", "Z"),
                "correlation_id": correlation_id,
            }
        if payload_type == "cash":
            cash_data = adapter.data_builder.cash(payload)
            seq = _send(
                transport,
                adapter,
                CMD_CASH,
                cash_data,
                seq,
                timeout_s,
                "cash",
                printer_id,
                correlation_id=correlation_id,
            )
            _SEQ_BY_PRINTER[printer_id] = seq
            return {
                "payload_type": "cash",
                "cash_type": payload.get("type"),
                "amount": payload.get("amount"),
                "correlation_id": correlation_id,
            }
        raise ValueError(f"Unsupported fiscal payload type: {payload_type}")
    except Exception as exc:
        log_error(
            "DATECS_FISCAL_JOB_FAILED",
            {
                "printer_id": printer_id,
                "payload_type": payload_type,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )
        raise
    finally:
        transport.close()


