from __future__ import annotations

from typing import Any, Dict, Iterable, List

from app.adapters.base import PrinterAdapter
from app.builders import DatecsDataBuilder, FP700MXDataBuilder


class DatecsBaseAdapter(PrinterAdapter):
    model = ""
    default_encoding = "cp1251"
    protocol_format = "hex4"
    status_length = 8

    @property
    def data_builder(self) -> DatecsDataBuilder:
        return FP700MXDataBuilder()

    default_commands = {
        "initialize": b"",
        "line_feed": b"\n",
        "cut": b"",
    }

    def _encoding(self) -> str:
        return str(self.config.get("encoding") or self.default_encoding)

    def _command(self, name: str) -> bytes:
        commands = dict(self.default_commands)
        commands.update(self.config.get("commands", {}))
        value = commands.get(name, b"")
        if isinstance(value, bytes):
            return value
        if isinstance(value, list):
            return bytes(value)
        if isinstance(value, str):
            value = value.strip().replace(" ", "")
            if not value:
                return b""
            try:
                return bytes.fromhex(value)
            except ValueError:
                return value.encode(self._encoding(), errors="ignore")
        return b""

    def _line_feed(self) -> bytes:
        return self._command("line_feed")

    def _line_width(self) -> int:
        return int(self.config.get("line_width") or 42)

    def _encode_lines(self, lines: Iterable[str]) -> bytes:
        encoding = self._encoding()
        line_feed = self._line_feed()
        chunks: List[bytes] = []
        for line in lines:
            chunks.append(line.encode(encoding, errors="ignore"))
            chunks.append(line_feed)
        return b"".join(chunks)

    def _format_receipt(self, payload: Dict[str, Any]) -> list[str]:
        lines: list[str] = []
        width = self._line_width()
        header = payload.get("header") or []
        items = payload.get("items") or []
        totals = payload.get("totals") or []
        footer = payload.get("footer") or []
        lines.extend([str(line) for line in header])
        if header:
            lines.append("-" * min(width, 42))
        for item in items:
            name = str(item.get("name", ""))
            qty = item.get("qty", 1)
            price = item.get("price", 0)
            total = item.get("total", qty * price)
            lines.append(f"{name} x{qty} @ {price} = {total}")
        if items:
            lines.append("-" * min(width, 42))
        for total_line in totals:
            label = total_line.get("label", "TOTAL") if isinstance(total_line, dict) else str(total_line)
            value = total_line.get("value", "") if isinstance(total_line, dict) else ""
            if value:
                lines.append(f"{label}: {value}")
            else:
                lines.append(str(label))
        lines.extend([str(line) for line in footer])
        return lines

    def build_lines(self, payload_type: str, payload: Dict[str, Any]) -> list[str]:
        if payload_type == "text":
            lines = payload.get("lines") or []
            return [str(line) for line in lines]
        if payload_type == "receipt":
            return self._format_receipt(payload)
        if payload_type == "test":
            return [
                "=== Datecs Test Print ===",
                f"Model: {self.model}",
                "Status: OK",
            ]
        raise ValueError(f"Unsupported payload type: {payload_type}")

    def build_payload(self, payload_type: str, payload: Dict[str, Any]) -> bytes:
        init = self._command("initialize")
        cut = self._command("cut")
        content = self._encode_lines(self.build_lines(payload_type, payload))
        return init + content + cut

    def build_test_print(self) -> bytes:
        return self.build_payload("test", {})
