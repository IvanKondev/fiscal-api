"""Data builder for the FP-2000 series (protocol 2.00BG, byte framing).

Models: FP-800, FP-2000, FP-650, SK1-21F, SK1-31F, FMP-10, FP-700.

Wire format: compact — fields are NOT uniformly TAB-separated.
Tax codes are letters 'A'–'H'.  Payment modes are letters 'P','N','C','D',…
Open-receipt uses COMMA separators.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import DatecsDataBuilder

_CYRILLIC_TAX = {"А": "A", "Б": "B", "В": "C", "Г": "D",
                 "Д": "E", "Е": "F", "Ж": "G", "З": "H"}
_DIGIT_TO_LETTER = {"1": "A", "2": "B", "3": "C", "4": "D",
                    "5": "E", "6": "F", "7": "G", "8": "H"}


def _tax_letter(code: Any) -> str:
    """Normalise any tax-group representation to a letter 'A'–'H'."""
    if code is None or code == "":
        return "A"
    v = str(code).strip().upper()
    v = _CYRILLIC_TAX.get(v, v)
    if v in _DIGIT_TO_LETTER:
        return _DIGIT_TO_LETTER[v]
    if v in _DIGIT_TO_LETTER.values():
        return v
    return "A"


def _payment_letter(value: Any) -> str:
    """Map payment type to FP-2000 letter code."""
    raw = str(value or "P").strip().upper()
    mapping = {
        "0": "P", "P": "P",        # cash
        "1": "D", "D": "D",        # card
        "2": "N", "N": "N",        # credit
        "3": "C", "C": "C",        # cheque
    }
    return mapping.get(raw, "P")


class FP2000DataBuilder(DatecsDataBuilder):
    """FP-2000 series — compact wire format."""

    # 0x30  Open receipt
    # <OpNum>,<Password>,<TillNum>[,<Invoice>][,<UNP>]
    def open_receipt(self, op_num: str, password: str, till: str,
                     invoice: str = "", nsale: str = "") -> str:
        parts = [op_num, password, till]
        if invoice:
            parts.append(invoice)
        if nsale:
            parts.append(nsale)
        return ",".join(parts)

    # 0x31  Sale
    # [<L1>][<Lf><L2>]<Tab><TaxCd><[Sign]Price>[*<Qwan>[#UN]][,Perc|;Abs]
    # OR  [<L1>]<Tab><Dept><Tab><[Sign]Price>[*<Qwan>[#UN]][,Perc|;Abs]
    def sale(self, item: Dict[str, Any]) -> str:
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError("Sale item requires name.")
        tax = _tax_letter(item.get("tax") or item.get("tax_code") or item.get("tax_group"))
        price = self.format_amount(item.get("price"))
        if not price:
            raise ValueError("Sale item requires price.")
        qty = item.get("qty")
        unit = str(item.get("unit") or "").strip()
        department = str(item.get("department") or "").strip()

        # Price*Qty[#Unit] suffix
        suffix = price
        if qty is not None and qty != "" and str(qty) != "1" and str(qty) != "1.000":
            suffix += f"*{qty}"
            if unit:
                suffix += f"#{unit}"
        elif unit:
            suffix += f"*1.000#{unit}"

        # Discount
        discount = item.get("discount")
        if discount is not None and discount != "":
            raw = str(discount).strip()
            if raw.endswith("%"):
                pct = raw.rstrip("%")
                suffix += f",{pct}"
            else:
                try:
                    n = float(raw)
                except ValueError:
                    n = None
                if n is not None and n != 0:
                    suffix += f";-{self.format_amount(abs(n))}"

        # Use department syntax or tax-letter syntax
        if department and department != "0":
            return f"{name}\t{department}\t{suffix}"
        return f"{name}\t{tax}{suffix}"

    # 0x35  Payment
    # [<Line1>][<Lf><Line2>]<Tab>[<PaidMode>][<Amount>]
    # PaidMode = P (cash), N (credit), C (cheque), D (card), …
    def payment(self, payment: Dict[str, Any]) -> str:
        if isinstance(payment, str):
            raise ValueError("Payment must be a dict with amount.")
        mode = _payment_letter(payment.get("type"))
        amount = self.format_amount(payment.get("amount"))
        if not amount:
            raise ValueError("Payment amount is required.")
        return f"\t{mode}{amount}"

    # 0x2A  Non-fiscal text
    # [<Tab><Font>[<Flags>]]<Text>
    def nonfiscal_text(self, text: str) -> str:
        return text

    # 0x36  Fiscal text
    # <Tab><Font>[<Flags>]<Text>
    def fiscal_text(self, text: str) -> str:
        return f"\t1{text}"

    # 0x46  Cash deposit/withdrawal
    # [<altcurrency>][<Amount>]   positive = deposit, negative = withdrawal
    def cash(self, payload: Dict[str, Any]) -> str:
        amount = payload.get("amount")
        if amount is None or amount == "":
            raise ValueError("Cash operation requires amount.")
        direction = str(payload.get("direction", "in")).strip().lower()
        currency = str(payload.get("currency") or "").strip().upper()
        num = abs(float(amount))
        if direction in {"out", "withdraw", "withdrawal"}:
            num = -num
        prefix = "*" if currency == "EUR" else ""
        return f"{prefix}{self.format_amount(num)}"

    # 0x45  Report
    # '0' = Z-report,  '2' = X-report
    def report(self, payload: Dict[str, Any]) -> str:
        option = payload.get("option")
        no_reset = bool(payload.get("no_reset") or payload.get("no_clear"))
        if option is not None:
            opt = str(option).strip().upper()
            if not opt:
                return ""
            if opt in {"Z", "0"}:
                opt = "0"
            elif opt in {"X", "2"}:
                opt = "2"
            if opt in {"?", "*"}:
                return opt
            suffix = "N" if no_reset else ""
            return f"{opt}{suffix}"
        rtype = str(payload.get("type", "x")).strip().lower()
        mapping = {"x": "2", "z": "0", "d": "D", "g": "G"}
        code = mapping.get(rtype)
        if code is None:
            raise ValueError("Report type must be 'x', 'z', 'd', or 'g'.")
        return code

    # 0x4A  Status
    def status_data(self) -> str:
        return "X"
