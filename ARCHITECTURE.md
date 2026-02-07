# FiscalAPI Architecture

## Overview

Print Gateway за Datecs фискални принтери. Всяка серия принтери има **свой DataBuilder**, който
знае точния wire-формат за командите на тази серия. Бизнес логиката (`datecs_fiscal.py`,
`datecs_print.py`) е обща — извиква `adapter.data_builder.sale(item)` и получава готов string,
без да знае кой принтер стои отдолу.

## Layers

```
┌─────────────────────────────────────────────────┐
│  React UI  (frontend/src/App.jsx)               │
├─────────────────────────────────────────────────┤
│  FastAPI  (app/api.py)                          │
├─────────────────────────────────────────────────┤
│  Fiscal / Print logic                           │
│  app/datecs_fiscal.py   app/datecs_print.py     │
├─────────────────────────────────────────────────┤
│  DataBuilder  (app/builders/)                   │
│  ┌──────────────────┐  ┌──────────────────┐     │
│  │ FP700MXDataBuilder│  │ FP2000DataBuilder │     │
│  │ (tab-separated)  │  │ (compact format) │     │
│  └──────────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────┤
│  Adapters  (app/adapters/)                      │
│  DatecsBaseAdapter → data_builder property       │
├─────────────────────────────────────────────────┤
│  Protocol  (app/datecs_protocol.py)             │
│  Framing: <01><LEN><SEQ><CMD><DATA><05><BCC><03>│
├─────────────────────────────────────────────────┤
│  Transport  (app/transports/)                   │
│  SerialTransport / UsbTransport                 │
└─────────────────────────────────────────────────┘
```

## DataBuilder Pattern

Коренът на архитектурата. Двете серии принтери използват **един и същ набор от команди**
(0x30, 0x31, 0x35, …), но с **напълно различен формат на DATA полето**.

### Пример: Команда 0x31 (Продажба)

| Серия | Формат | Пример |
|-------|--------|--------|
| **FP-700MX** | `{Name}<TAB>{TaxDigit}<TAB>{Price}<TAB>{Qty}<TAB>…` | `Кафе\t2\t2.50\t1.000\t\t\t0\t` |
| **FP-2000** | `{Name}<TAB>{TaxLetter}{Price}[*{Qty}]` | `Кафе\tB2.50` |

### Пример: Команда 0x30 (Отваряне на бон)

| Серия | Формат | Пример |
|-------|--------|--------|
| **FP-700MX** | `{Op}<TAB>{Pwd}<TAB>{Till}<TAB>{Invoice}<TAB>` | `1\t0000\t1\t\t` |
| **FP-2000** | `{Op},{Pwd},{Till}[,{Invoice}]` | `1,0000,1` |

### Пример: Команда 0x35 (Плащане)

| Серия | Формат | Пример |
|-------|--------|--------|
| **FP-700MX** | `{ModeDigit}<TAB>{Amount}<TAB>{Type}<TAB>` | `0\t5.00\t\t` |
| **FP-2000** | `<TAB>{ModeLetter}{Amount}` | `\tP5.00` |

### Абстрактен базов клас

```python
# app/builders/base.py
class DatecsDataBuilder(ABC):
    def open_receipt(op_num, password, till, invoice, nsale) -> str
    def sale(item: dict) -> str
    def payment(payment: dict) -> str
    def nonfiscal_text(text: str) -> str
    def fiscal_text(text: str) -> str
    def cash(payload: dict) -> str
    def report(payload: dict) -> str
    def status_data() -> str
```

Всеки адаптер връща правилния builder чрез property:

```python
class DatecsBaseAdapter:
    @property
    def data_builder(self) -> DatecsDataBuilder:
        return FP700MXDataBuilder()

class DatecsFP2000BaseAdapter(DatecsBaseAdapter):
    @property
    def data_builder(self) -> DatecsDataBuilder:
        return FP2000DataBuilder()
```

## Supported Printer Series

### FP-700MX Series (Protocol 2.08)

**Doc:** `Docs/datecs_fp700mx.md`
**Models:** FP-700X, FP-700MX, FMP-350X, FMP-55X, WP-500X, WP-50X, DP-25X, DP-150X, DP-05C, WP-25X
**Wire format:** TAB-separated fields, digit tax codes (1–8), digit payment modes (0–5)
**Protocol:** hex4 framing (4 ASCII hex digits for LEN/CMD), 8-byte status

### FP-2000 Series (Protocol 2.00BG)

**Doc:** `Docs/fp2000.md`
**Models:** FP-2000, FP-800, FP-650, SK1-21F, SK1-31F, FMP-10, FP-700 (v2.00BG)
**Wire format:** Compact — comma/tab mixed separators, letter tax codes (A–H), letter payment modes (P/N/C/D)
**Protocol:** byte framing (1 byte for LEN/CMD), 6-byte status

## Adapter Hierarchy

```
PrinterAdapter (base.py)
└── DatecsBaseAdapter (datecs_base.py)               → FP700MXDataBuilder
    ├── DatecsFP700MXAdapter (FP-700 series)
    │   └── DatecsOneToOneAdapter
    │       ├── DatecsFMP350XAdapter
    │       ├── DatecsFP700XAdapter
    │       ├── DatecsWP500XAdapter
    │       └── …per-model
    └── DatecsFP2000BaseAdapter (FP-2000 series)     → FP2000DataBuilder
        ├── DatecsFP2000Adapter
        ├── DatecsFP800Adapter
        ├── DatecsFP650Adapter
        └── …per-model
```

## Key Commands

| Code | Name | Description |
|------|------|-------------|
| `0x26` | Open service receipt | Нефискален бон |
| `0x27` | Close service receipt | Затваряне |
| `0x2A` | Print text | Свободен текст в нефискален бон |
| `0x30` | Open fiscal receipt | Отваряне на фискален бон |
| `0x31` | Sale | Продажба на артикул |
| `0x35` | Payment | Плащане |
| `0x38` | Close fiscal receipt | Затваряне на фискален бон |
| `0x3C` | Cancel receipt | Отказ на бон |
| `0x3D` | Set date/time | Настройка на часовник |
| `0x3E` | Read date/time | Четене на часовник |
| `0x45` | Daily report | Z/X отчет |
| `0x46` | Cash in/out | Служебен внос/износ |
| `0x4A` | Status | Статус на принтера |

## Adding a New Printer Series

1. **Създай builder** — `app/builders/new_series.py`:
```python
from app.builders.base import DatecsDataBuilder

class NewSeriesDataBuilder(DatecsDataBuilder):
    def open_receipt(self, op_num, password, till, invoice="", nsale=""):
        return ...  # wire format per documentation
    def sale(self, item):
        return ...
    # … implement all abstract methods
```

2. **Създай base adapter** — `app/adapters/datecs_new_series_base.py`:
```python
from app.adapters.datecs_base import DatecsBaseAdapter
from app.builders.new_series import NewSeriesDataBuilder

class DatecsNewSeriesBaseAdapter(DatecsBaseAdapter):
    protocol_format = "..."
    status_length = ...

    @property
    def data_builder(self):
        return NewSeriesDataBuilder()
```

3. **Регистрирай** в `app/adapters/__init__.py` и добави модели в UI.

Нищо друго не се променя — `datecs_fiscal.py` и `datecs_print.py` работят автоматично
с новата серия, защото извикват `adapter.data_builder.*()`.

## Status Bytes (6 bytes, shared by both series)

| Byte | Bit | Flag |
|------|-----|------|
| 0 | 6 | Cover open |
| 0 | 5 | General error |
| 0 | 4 | Printing unit fault |
| 0 | 2 | Clock not set |
| 0 | 1 | Invalid command |
| 0 | 0 | Syntax error |
| 1 | 4 | Storno receipt open |
| 1 | 1 | Command not allowed |
| 2 | 5 | Service receipt open |
| 2 | 3 | Fiscal receipt open |
| 2 | 1 | Low paper |
| 2 | 0 | No paper |
| 4 | 6 | Head overheated |
| 4 | 4 | Fiscal memory full |
| 5 | 3 | Fiscal mode |

## References

- FP-700MX docs: `Docs/datecs_fp700mx.md`
- FP-2000 docs: `Docs/fp2000.md`
- Наредба Н-18 на НАП — регулации за фискални устройства
