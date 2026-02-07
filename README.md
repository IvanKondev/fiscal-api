# FiscalAPI — Print Gateway за Datecs фискални принтери

Локален Python service + React UI за управление на Datecs фискални принтери по Serial/USB.
Поддържа фискални бонове, сторно, Z/X отчети, служебни бонове и служебен внос/износ.

## Поддържани серии принтери

| Серия | Модели | Протокол |
|-------|--------|----------|
| **FP-700MX** | FP-700X, FP-700MX, FMP-350X, FMP-55X, WP-500X, WP-50X, DP-25X, DP-150X, DP-05C, WP-25X | 2.08, hex4 framing |
| **FP-2000** | FP-2000, FP-800, FP-650, SK1-21F, SK1-31F, FMP-10, FP-700 (v2.00BG) | 2.00BG, byte framing |

## Технологии

- **Backend:** Python 3.11+, FastAPI, uvicorn
- **Database:** SQLite (printers, jobs, logs)
- **Serial:** pyserial (COM/RS-232)
- **USB:** pyusb (опционално)
- **Frontend:** React + Vite (билд в `app/static`)

## Структура на проекта

```
app/
  builders/              ← DataBuilder per printer series
    base.py              ← DatecsDataBuilder (abstract)
    fp700mx.py           ← FP700MXDataBuilder
    fp2000.py            ← FP2000DataBuilder
  adapters/              ← Printer adapters
    base.py              ← PrinterAdapter (abstract)
    datecs_base.py       ← DatecsBaseAdapter
    datecs_fp2000_base.py
    datecs_fp700mx.py
    ...per-model adapters
  transports/            ← Serial / USB transport
  api.py                 ← FastAPI endpoints
  datecs_protocol.py     ← Low-level protocol (framing, BCC, NAK/SYN)
  datecs_fiscal.py       ← Fiscal operations (receipt, payment, report)
  datecs_print.py        ← Non-fiscal printing
  db.py                  ← SQLite storage
  job_queue.py           ← Background job queue
  main.py                ← App entry point
frontend/                ← React SPA
Docs/                    ← Protocol documentation
```

## Инсталация

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### UI build

```bash
cd frontend
npm install
npm run build
```

## Стартиране

```bash
python -m app
```

UI: **http://127.0.0.1:8787**

## API endpoints

| Method | Endpoint | Описание |
|--------|----------|----------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/printers` | Списък принтери |
| `POST` | `/api/printers` | Добави принтер |
| `PUT` | `/api/printers/{id}` | Редактирай принтер |
| `DELETE` | `/api/printers/{id}` | Изтрий принтер |
| `POST` | `/api/printers/{id}/test-print` | Тестов печат |
| `GET` | `/api/printers/{id}/status` | Статус на принтера |
| `GET` | `/api/printers/{id}/datetime` | Четене на дата/час |
| `POST` | `/api/printers/{id}/datetime/sync` | Синхронизация на часовник |
| `POST` | `/api/printers/{id}/cancel_receipt` | Отказ на отворен бон |
| `POST` | `/api/jobs` | Създай job (печат) |
| `GET` | `/api/jobs?limit=50` | Списък jobs |
| `GET` | `/api/jobs/{id}` | Детайли за job |
| `GET` | `/api/logs?limit=200` | Системни логове |
| `GET` | `/api/tools/serial-ports` | Налични COM портове |
| `GET` | `/api/tools/models` | Поддържани модели |

## Фискален бон

```json
{
  "printer_id": 1,
  "payload_type": "fiscal_receipt",
  "payload": {
    "operator": {"id": "1", "password": "0000", "till": "1"},
    "items": [
      {"name": "Кафе", "tax": "B", "price": "2.50", "qty": "1"},
      {"name": "Чай", "tax": "B", "price": "3.20", "qty": "2"}
    ],
    "payments": [{"type": "P", "amount": "8.90"}]
  }
}
```

- **tax**: `A`–`H` (букви) или `1`–`8` (цифри) — builder-ът конвертира автоматично.
- **type** (плащане): `P` (в брой), `D` (карта), `N` (кредит), `C` (чек).
- **nsale** (по избор): УНП, 21 символа.
- **invoice** (по избор): `true` за разширен бон (фактура).

## Служебен бон (нефискален)

```json
{
  "printer_id": 1,
  "payload_type": "text",
  "payload": {"lines": ["Ред 1", "Ред 2", "Ред 3"]}
}
```

## Z/X отчет

```json
{
  "printer_id": 1,
  "payload_type": "report",
  "payload": {"type": "z"}
}
```

## Служебен внос/износ

```json
{
  "printer_id": 1,
  "payload_type": "cash",
  "payload": {"amount": 10.00, "direction": "in"}
}
```

## Auto-detect

UI → **Tools → Auto-detect Datecs** — сканира COM портове и baudrate-и, връща кандидати.

## Dry-run режим

- Global: `PRINT_GATEWAY_DRY_RUN=true`
- Per-printer: `dry_run=true`

## PyInstaller build (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --name print-gateway \
  --add-data "app/static;app/static" \
  app/__main__.py
```

## Environment variables

| Променлива | Описание | Default |
|------------|----------|---------|
| `PRINT_GATEWAY_PORT` | HTTP порт | `8787` |
| `PRINT_GATEWAY_DB` | SQLite path | `data/print_gateway.sqlite` |
| `PRINT_GATEWAY_DRY_RUN` | Dry-run mode | `false` |
| `PRINT_GATEWAY_JOB_TIMEOUT` | Job timeout (s) | `15` |
| `PRINT_GATEWAY_JOB_RETRIES` | Max retries | `1` |
| `PRINT_GATEWAY_POLL_INTERVAL` | Poll interval (s) | `1` |
| `PRINT_GATEWAY_DATECS_BAUDRATES` | Baudrate-и за auto-detect | `9600,...,115200` |
| `PRINT_GATEWAY_DETECT_TIMEOUT_MS` | Detect timeout (ms) | `600` |
