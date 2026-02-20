"""Data builder for the FP-700MX series (protocol 2.08, hex4 framing).

Models: FMP-350X, FMP-55X, FP-700X, FP-700XE, WP-500X, WP-50X,
        DP-25X, WP-25X, DP-150X, DP-05C.

Wire format: all fields are TAB-separated (<SEP> = 0x09).
Tax codes are digits '1'–'8'.  Payment modes are digits '0'–'5'.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import DatecsDataBuilder

# Cyrillic → Latin tax letter, then letter → digit
_CYRILLIC_TAX = {"А": "A", "Б": "B", "В": "C", "Г": "D",
                 "Д": "E", "Е": "F", "Ж": "G", "З": "H"}
_LETTER_TO_DIGIT = {"A": "1", "B": "2", "C": "3", "D": "4",
                    "E": "5", "F": "6", "G": "7", "H": "8"}


def _tax_digit(code: Any) -> str:
    """Normalise any tax-group representation to a digit '1'–'8'."""
    if code is None or code == "":
        return "1"
    v = str(code).strip().upper()
    v = _CYRILLIC_TAX.get(v, v)
    if v in _LETTER_TO_DIGIT:
        return _LETTER_TO_DIGIT[v]
    if v.isdigit() and v in _LETTER_TO_DIGIT.values():
        return v
    return _LETTER_TO_DIGIT.get(v, "1")


def _payment_mode(value: Any) -> str:
    raw = str(value or "P").strip().upper()
    if raw.isdigit():
        return raw
    return {"P": "0", "C": "1", "N": "2"}.get(raw, "0")


class FP700MXDataBuilder(DatecsDataBuilder):
    """FP-700MX series — TAB-separated fields."""

    # 0x30  Open receipt
    # Syntax 1: {OpCode}<SEP>{OpPwd}<SEP>{TillNmb}<SEP>{Invoice}<SEP>
    # Syntax 2: {OpCode}<SEP>{OpPwd}<SEP>{NSale}<SEP>{TillNmb}<SEP>{Invoice}<SEP>
    def open_receipt(self, op_num: str, password: str, till: str,
                     invoice: str = "", nsale: str = "") -> str:
        if nsale:
            return f"{op_num}\t{password}\t{nsale}\t{till}\t{invoice}\t"
        return f"{op_num}\t{password}\t{till}\t{invoice}\t"

    # 0x31  Sale
    # {PluName}<SEP>{TaxCd}<SEP>{Price}<SEP>{Qty}<SEP>{DiscType}<SEP>{DiscVal}<SEP>{Dept}<SEP>[{Unit}<SEP>]
    def sale(self, item: Dict[str, Any]) -> str:
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError("Sale item requires name.")
        tax = _tax_digit(item.get("tax") or item.get("tax_code") or item.get("tax_group"))
        price = self.format_amount(item.get("price"))
        if not price:
            raise ValueError("Sale item requires price.")
        qty = str(item.get("qty")) if item.get("qty") not in (None, "") else "1.000"
        department = str(item.get("department") or "").strip() or "0"
        unit = str(item.get("unit") or "").strip()

        discount_type, discount_value = "", ""
        discount = item.get("discount")
        if discount is not None and discount != "":
            raw = str(discount).strip()
            if raw.endswith("%"):
                discount_type, discount_value = "2", raw.rstrip("%")
            else:
                try:
                    n = float(raw)
                except ValueError:
                    n = None
                if n is not None and n != 0:
                    discount_type = "4"
                    discount_value = self.format_amount(abs(n))

        fields = [name, tax, price, qty, discount_type, discount_value, department]
        if unit:
            fields.append(unit)
        return "\t".join(fields) + "\t"

    # 0x35  Payment
    # {PaidMode}<SEP>{Amount}<SEP>{Type}<SEP>
    def payment(self, payment: Dict[str, Any]) -> str:
        if isinstance(payment, str):
            raise ValueError("Payment must be a dict with amount.")
        mode = _payment_mode(payment.get("type"))
        amount = self.format_amount(payment.get("amount"))
        if not amount:
            raise ValueError("Payment amount is required.")
        return f"{mode}\t{amount}\t\t"

    # 0x2A  Non-fiscal text
    # {Text}<SEP>{Bold}<SEP>{Italic}<SEP>{Height}<SEP>{Underline}<SEP>{alignment}<SEP>
    def nonfiscal_text(self, text: str) -> str:
        return f"{text}\t\t\t\t\t\t"

    # 0x36  Fiscal text
    # {Text}<SEP>{Bold}<SEP>{Italic}<SEP>{DoubleH}<SEP>{Underline}<SEP>{alignment}<SEP>
    def fiscal_text(self, text: str) -> str:
        return f"{text}\t\t\t\t\t\t"

    # 0x46  Cash deposit/withdrawal
    # {Type}<SEP>{Amount}<SEP>
    def cash(self, payload: Dict[str, Any]) -> str:
        amount = payload.get("amount")
        if amount is None or amount == "":
            raise ValueError("Cash operation requires amount.")
        direction = str(payload.get("direction", "in")).strip().lower()
        currency = str(payload.get("currency") or "").strip().upper()
        if direction in {"in", "deposit"}:
            cash_type = "2" if currency == "EUR" else "0"
        elif direction in {"out", "withdraw", "withdrawal"}:
            cash_type = "3" if currency == "EUR" else "1"
        else:
            raise ValueError("Cash direction must be 'in' or 'out'.")
        return f"{cash_type}\t{self.format_amount(amount)}\t"

    # 0x45  Report
    def report(self, payload: Dict[str, Any]) -> str:
        option = payload.get("option")
        no_reset = bool(payload.get("no_reset") or payload.get("no_clear"))
        if option is not None:
            opt = str(option).strip().upper()
            if not opt:
                return ""
            if opt in {"0", "Z"}:
                opt = "Z"
            elif opt in {"2", "X"}:
                opt = "X"
            return f"{opt}\t"
        rtype = str(payload.get("type", "x")).strip().lower()
        mapping = {"x": "X", "z": "Z", "d": "D", "g": "G"}
        code = mapping.get(rtype)
        if code is None:
            raise ValueError("Report type must be 'x', 'z', 'd', or 'g'.")
        return f"{code}\t"

    # 0x4A  Status
    def status_data(self) -> str:
        return "0"
