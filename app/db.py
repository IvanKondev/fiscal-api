from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from app.settings import DATA_DIR, DB_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS printers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT NOT NULL,
                transport TEXT NOT NULL,
                port TEXT,
                baudrate INTEGER DEFAULT 9600,
                data_bits INTEGER DEFAULT 8,
                parity TEXT DEFAULT 'N',
                stop_bits REAL DEFAULT 1,
                timeout_ms INTEGER DEFAULT 5000,
                ip_address TEXT,
                tcp_port INTEGER DEFAULT 4999,
                enabled INTEGER DEFAULT 1,
                dry_run INTEGER DEFAULT 0,
                config_json TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        # Migration: add LAN columns to existing databases
        try:
            conn.execute("ALTER TABLE printers ADD COLUMN ip_address TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE printers ADD COLUMN tcp_port INTEGER DEFAULT 4999")
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                printer_id INTEGER NOT NULL,
                payload_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                retries INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                result_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                FOREIGN KEY(printer_id) REFERENCES printers(id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                context_json TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def _printer_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = dict(row)
    data["enabled"] = bool(data["enabled"])
    data["dry_run"] = bool(data["dry_run"])
    data["config"] = json.loads(data.get("config_json") or "{}")
    data.pop("config_json", None)
    return data


def _job_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = dict(row)
    data["payload"] = json.loads(data.get("payload_json") or "{}")
    data.pop("payload_json", None)
    result_raw = data.get("result_json")
    data["result"] = json.loads(result_raw) if result_raw else None
    data.pop("result_json", None)
    return data


def _log_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    data = dict(row)
    context_raw = data.get("context_json")
    data["context"] = json.loads(context_raw) if context_raw else None
    data.pop("context_json", None)
    return data


def list_printers() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM printers ORDER BY id ASC").fetchall()
    return [_printer_from_row(row) for row in rows]


def get_printer(printer_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM printers WHERE id = ?", (printer_id,)).fetchone()
    return _printer_from_row(row) if row else None


def create_printer(data: Dict[str, Any]) -> Dict[str, Any]:
    now = now_iso()
    config_json = json.dumps(data.get("config") or {}, ensure_ascii=False)
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO printers
            (name, model, transport, port, baudrate, data_bits, parity, stop_bits, timeout_ms,
             ip_address, tcp_port, enabled, dry_run, config_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["model"],
                data["transport"],
                data.get("port"),
                data.get("baudrate", 9600),
                data.get("data_bits", 8),
                data.get("parity", "N"),
                data.get("stop_bits", 1),
                data.get("timeout_ms", 5000),
                data.get("ip_address"),
                data.get("tcp_port", 4999),
                1 if data.get("enabled", True) else 0,
                1 if data.get("dry_run", False) else 0,
                config_json,
                now,
                now,
            ),
        )
        printer_id = cur.lastrowid
        conn.commit()
    return get_printer(int(printer_id))


def update_printer(printer_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not data:
        return get_printer(printer_id)
    fields = []
    values: List[Any] = []
    mapping = {
        "name": "name",
        "model": "model",
        "transport": "transport",
        "port": "port",
        "baudrate": "baudrate",
        "data_bits": "data_bits",
        "parity": "parity",
        "stop_bits": "stop_bits",
        "timeout_ms": "timeout_ms",
        "ip_address": "ip_address",
        "tcp_port": "tcp_port",
        "enabled": "enabled",
        "dry_run": "dry_run",
        "config": "config_json",
    }
    for key, column in mapping.items():
        if key not in data:
            continue
        value = data[key]
        if key == "config":
            value = json.dumps(value or {}, ensure_ascii=False)
        if key in {"enabled", "dry_run"}:
            value = 1 if value else 0
        fields.append(f"{column} = ?")
        values.append(value)
    if not fields:
        return get_printer(printer_id)
    fields.append("updated_at = ?")
    values.append(now_iso())
    values.append(printer_id)
    query = f"UPDATE printers SET {', '.join(fields)} WHERE id = ?"
    with _connect() as conn:
        conn.execute(query, values)
        conn.commit()
    return get_printer(printer_id)


def delete_printer(printer_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM printers WHERE id = ?", (printer_id,))
        conn.commit()


def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_job_from_row(row) for row in rows]


def list_jobs_by_status(status: str, limit: int = 20) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE status = ? ORDER BY created_at ASC LIMIT ?",
            (status, limit),
        ).fetchall()
    return [_job_from_row(row) for row in rows]


def get_job(job_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return _job_from_row(row) if row else None


def create_job(printer_id: int, payload_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    now = now_iso()
    payload_json = json.dumps(payload or {}, ensure_ascii=False)
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO jobs
            (printer_id, payload_type, payload_json, status, retries, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', 0, ?, ?)
            """,
            (printer_id, payload_type, payload_json, now, now),
        )
        job_id = cur.lastrowid
        conn.commit()
    return get_job(int(job_id))


def update_job(job_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not data:
        return get_job(job_id)
    fields = []
    values: List[Any] = []
    mapping = {
        "payload": "payload_json",
        "result": "result_json",
        "status": "status",
        "retries": "retries",
        "error": "error",
        "started_at": "started_at",
        "finished_at": "finished_at",
    }
    for key, column in mapping.items():
        if key not in data:
            continue
        value = data[key]
        if key in ("payload", "result"):
            value = json.dumps(value or {}, ensure_ascii=False) if value else None
        fields.append(f"{column} = ?")
        values.append(value)
    if not fields:
        return get_job(job_id)
    fields.append("updated_at = ?")
    values.append(now_iso())
    values.append(job_id)
    query = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
    with _connect() as conn:
        conn.execute(query, values)
        conn.commit()
    return get_job(job_id)


def create_log(level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    now = now_iso()
    context_json = json.dumps(context, ensure_ascii=False) if context else None
    with _connect() as conn:
        conn.execute(
            "INSERT INTO logs (level, message, context_json, created_at) VALUES (?, ?, ?, ?)",
            (level, message, context_json, now),
        )
        conn.commit()


def list_logs(limit: int = 200) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_log_from_row(row) for row in rows]
