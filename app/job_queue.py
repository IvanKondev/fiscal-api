from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from app.db import get_printer, list_jobs_by_status, now_iso, update_job
from app.app_logging import log_error, log_info
from app.printer_service import send_payload
from app.settings import JOB_MAX_RETRIES, JOB_POLL_INTERVAL, JOB_TIMEOUT_SECONDS


class JobQueue:
    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._active_jobs: set[int] = set()
        self._locks: dict[int, asyncio.Lock] = {}

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task:
            await self._task

    def _get_lock(self, printer_id: int) -> asyncio.Lock:
        if printer_id not in self._locks:
            self._locks[printer_id] = asyncio.Lock()
        return self._locks[printer_id]

    def get_lock(self, printer_id: int) -> asyncio.Lock:
        return self._get_lock(printer_id)

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            await self._dispatch()
            await asyncio.sleep(JOB_POLL_INTERVAL)

    async def _dispatch(self) -> None:
        queued_jobs = list_jobs_by_status("queued", limit=20)
        for job in queued_jobs:
            job_id = int(job["id"])
            if job_id in self._active_jobs:
                continue
            self._active_jobs.add(job_id)
            asyncio.create_task(self._process_job(job))

    async def _process_job(self, job: Dict[str, Any]) -> None:
        job_id = int(job["id"])
        printer_id = int(job["printer_id"])
        try:
            printer = get_printer(printer_id)
            if not printer or not printer.get("enabled"):
                update_job(
                    job_id,
                    {
                        "status": "failed",
                        "error": "Printer not found or disabled",
                        "finished_at": now_iso(),
                    },
                )
                log_error("JOB_FAILED_PRINTER", {"job_id": job_id, "printer_id": printer_id})
                return
            lock = self._get_lock(printer_id)
            async with lock:
                update_job(job_id, {"status": "printing", "started_at": now_iso(), "error": None})
                log_info("JOB_PRINTING", {"job_id": job_id, "printer_id": printer_id})
                try:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            send_payload,
                            printer,
                            job.get("payload_type", "text"),
                            job.get("payload", {}),
                        ),
                        timeout=JOB_TIMEOUT_SECONDS,
                    )
                except Exception as exc:  # noqa: BLE001
                    await self._handle_failure(job, exc)
                else:
                    update_job(
                        job_id,
                        {
                            "status": "success",
                            "finished_at": now_iso(),
                            "error": None,
                            "result": result,
                        },
                    )
                    log_info("JOB_SUCCESS", {"job_id": job_id, "printer_id": printer_id, "result": result})
        finally:
            self._active_jobs.discard(job_id)

    async def _handle_failure(self, job: Dict[str, Any], exc: Exception) -> None:
        job_id = int(job["id"])
        retries = int(job.get("retries", 0))
        error_message = str(exc)
        if retries < JOB_MAX_RETRIES:
            update_job(
                job_id,
                {
                    "status": "queued",
                    "retries": retries + 1,
                    "error": error_message,
                    "started_at": None,
                },
            )
            log_error("JOB_RETRY", {"job_id": job_id, "error": error_message})
        else:
            update_job(
                job_id,
                {
                    "status": "failed",
                    "retries": retries + 1,
                    "error": error_message,
                    "finished_at": now_iso(),
                },
            )
            log_error("JOB_FAILED", {"job_id": job_id, "error": error_message})
