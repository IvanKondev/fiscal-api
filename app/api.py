from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException, Query

from app.adapters import get_adapter, list_supported_models
from app.adapters.datecs_base import DatecsBaseAdapter
from app.db import (
    create_job,
    create_printer,
    delete_printer,
    get_job,
    get_printer,
    list_jobs,
    list_logs,
    list_printers,
    now_iso,
    update_job,
    update_printer,
)
from app.app_logging import log_error, log_info
from app.models import (
    JobCreate,
    JobOut,
    LogOut,
    PrinterCreate,
    PrinterOut,
    PrinterUpdate,
)
from app.datecs_fiscal import _cancel_receipt
from app.detect import detect_printer_on_lan, detect_printer_on_port
from app.printer_service import send_payload
from app.settings import JOB_TIMEOUT_SECONDS
from app.state import job_queue
from app.transports.serial_transport import list_serial_ports

router = APIRouter()


def _model_dump(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


def _validate_model(model: str | None) -> None:
    if model is None:
        return
    if model.lower() not in list_supported_models():
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported model '{model}'. Supported: {', '.join(list_supported_models())}",
        )


def _validate_transport(transport: str | None) -> None:
    if transport is None:
        return
    if transport.lower() not in {"serial", "usb"}:
        raise HTTPException(status_code=400, detail="Transport must be 'serial' or 'usb'.")


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/printers", response_model=List[PrinterOut])
def printers_list() -> List[Dict[str, Any]]:
    return list_printers()


@router.get("/printers/{printer_id}", response_model=PrinterOut)
def printer_get(printer_id: int) -> Dict[str, Any]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    return printer


@router.post("/printers", response_model=PrinterOut)
def printer_create(printer: PrinterCreate) -> Dict[str, Any]:
    payload = _model_dump(printer)
    _validate_model(payload.get("model"))
    _validate_transport(payload.get("transport"))
    return create_printer(payload)


@router.put("/printers/{printer_id}", response_model=PrinterOut)
def printer_update(printer_id: int, printer: PrinterUpdate) -> Dict[str, Any]:
    payload = _model_dump(printer)
    _validate_model(payload.get("model"))
    _validate_transport(payload.get("transport"))
    updated = update_printer(printer_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Printer not found")
    return updated


@router.delete("/printers/{printer_id}")
def printer_delete(printer_id: int) -> Dict[str, str]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    delete_printer(printer_id)
    return {"status": "deleted"}


@router.post("/printers/{printer_id}/refresh-info")
async def printer_refresh_info(printer_id: int) -> Dict[str, Any]:
    """Re-detect printer and update SN, firmware, fiscal_memory_number in DB."""
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    transport_type = (printer.get("transport") or "serial").lower()
    try:
        if transport_type == "lan":
            result = await asyncio.to_thread(
                detect_printer_on_lan,
                printer.get("ip_address", ""),
                printer.get("tcp_port", 4999),
            )
        else:
            result = await asyncio.to_thread(
                detect_printer_on_port,
                printer.get("port", ""),
                printer.get("baudrate"),
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if not result.get("detected"):
        raise HTTPException(status_code=404, detail=result.get("error", "Printer not detected"))
    update_data = {}
    if result.get("serial_number"):
        update_data["serial_number"] = result["serial_number"]
    if result.get("firmware"):
        update_data["firmware"] = result["firmware"]
    if result.get("fiscal_memory_number"):
        update_data["fiscal_memory_number"] = result["fiscal_memory_number"]
    if update_data:
        updated = update_printer(printer_id, update_data)
        log_info("PRINTER_INFO_REFRESHED", {"printer_id": printer_id, **update_data})
        return updated
    return get_printer(printer_id)


@router.post("/printers/{printer_id}/test-print")
async def printer_test_print(printer_id: int) -> Dict[str, str]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    if not printer.get("enabled"):
        raise HTTPException(status_code=400, detail="Printer is disabled")
    lock = job_queue.get_lock(printer_id)
    async with lock:
        try:
            await asyncio.wait_for(
                asyncio.to_thread(send_payload, printer, "test", {}),
                timeout=JOB_TIMEOUT_SECONDS,
            )
        except Exception as exc:  # noqa: BLE001
            log_error("TEST_PRINT_FAILED", {"printer_id": printer_id, "error": str(exc)})
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    log_info("TEST_PRINT_SUCCESS", {"printer_id": printer_id})
    return {"status": "ok"}


@router.post("/jobs", response_model=JobOut)
def job_create(job: JobCreate) -> Dict[str, Any]:
    payload = _model_dump(job)
    printer = get_printer(payload["printer_id"])
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    if not printer.get("enabled"):
        raise HTTPException(status_code=400, detail="Printer is disabled")
    return create_job(payload["printer_id"], payload["payload_type"], payload["payload"])


@router.get("/jobs", response_model=List[JobOut])
def jobs_list(limit: int = Query(50, ge=1, le=200)) -> List[Dict[str, Any]]:
    return list_jobs(limit)


@router.get("/jobs/{job_id}", response_model=JobOut)
def job_get(job_id: int) -> Dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/jobs/{job_id}/retry", response_model=JobOut)
def job_retry(job_id: int) -> Dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] not in {"failed", "queued"}:
        raise HTTPException(status_code=400, detail="Only failed or queued jobs can be retried")
    updated = update_job(job_id, {"status": "queued", "error": None, "started_at": None, "finished_at": None})
    log_info("JOB_MANUAL_RETRY", {"job_id": job_id, "user_action": True})
    return updated


@router.post("/jobs/{job_id}/cancel", response_model=JobOut)
def job_cancel(job_id: int) -> Dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "printing":
        raise HTTPException(status_code=400, detail="Cannot cancel a job that is currently printing")
    updated = update_job(job_id, {"status": "failed", "error": "Cancelled by user", "finished_at": now_iso()})
    log_info("JOB_MANUAL_CANCEL", {"job_id": job_id, "user_action": True})
    return updated


@router.get("/logs", response_model=List[LogOut])
def logs_list(limit: int = Query(200, ge=1, le=500)) -> List[Dict[str, Any]]:
    return list_logs(limit)


@router.get("/tools/serial-ports")
def serial_ports() -> Dict[str, Any]:
    return {"ports": list_serial_ports()}


@router.post("/tools/detect-printer")
async def detect_printer(body: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    port = body.get("port")
    if not port:
        raise HTTPException(status_code=400, detail="Port is required")
    baudrate = body.get("baudrate")
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(detect_printer_on_port, port, baudrate),
            timeout=15,
        )
        return result
    except asyncio.TimeoutError:
        return {"detected": False, "port": port, "error": "Detection timed out"}
    except Exception as exc:
        log_error("DETECT_ENDPOINT_ERROR", {"port": port, "error": str(exc)})
        return {"detected": False, "port": port, "error": str(exc)}


@router.post("/tools/detect-printer-lan")
async def detect_printer_lan(body: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    ip_address = body.get("ip_address")
    if not ip_address:
        raise HTTPException(status_code=400, detail="ip_address is required")
    tcp_port = int(body.get("tcp_port", 4999))
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(detect_printer_on_lan, ip_address, tcp_port),
            timeout=15,
        )
        return result
    except asyncio.TimeoutError:
        return {"detected": False, "ip_address": ip_address, "tcp_port": tcp_port, "error": "Detection timed out"}
    except Exception as exc:
        log_error("DETECT_LAN_ENDPOINT_ERROR", {"ip_address": ip_address, "error": str(exc)})
        return {"detected": False, "ip_address": ip_address, "tcp_port": tcp_port, "error": str(exc)}


@router.post("/printers/{printer_id}/cancel_receipt")
def cancel_receipt(printer_id: int) -> Dict[str, Any]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    job = create_job({
        "printer_id": printer_id,
        "operation": "cancel_receipt",
        "payload": {"reason": "Manual cancellation by user"},
        "status": "printing",
    })
    
    try:
        adapter = get_adapter(printer["model"], printer.get("config") or {})
        if not isinstance(adapter, DatecsBaseAdapter):
            update_job(job["id"], {"status": "failed", "error": "Only Datecs printers support cancel receipt", "finished_at": now_iso()})
            raise HTTPException(status_code=400, detail="Only Datecs printers support cancel receipt")
        
        from app.transports.factory import create_transport
        try:
            transport = create_transport(printer)
        except ValueError as exc:
            update_job(job["id"], {"status": "failed", "error": str(exc), "finished_at": now_iso()})
            raise HTTPException(status_code=400, detail=str(exc))
        transport.open()
        try:
            from app.datecs_fiscal import _SEQ_BY_PRINTER
            seq = _SEQ_BY_PRINTER.get(printer_id, 0x20)
            timeout_s = int(printer.get("timeout_ms", 5000)) / 1000
            seq = _cancel_receipt(transport, adapter, seq, timeout_s, printer_id)
            _SEQ_BY_PRINTER[printer_id] = seq
            log_info("MANUAL_CANCEL_RECEIPT", {"printer_id": printer_id, "user_action": True, "job_id": job["id"]})
            update_job(job["id"], {"status": "success", "finished_at": now_iso()})
            return {"success": True, "message": "Receipt cancelled", "job_id": job["id"]}
        finally:
            transport.close()
    except HTTPException:
        raise
    except Exception as e:
        log_error("MANUAL_CANCEL_FAILED", {"printer_id": printer_id, "error": str(e), "job_id": job["id"]})
        update_job(job["id"], {"status": "failed", "error": str(e), "finished_at": now_iso()})
        raise HTTPException(status_code=500, detail=f"Failed to cancel receipt: {str(e)}")


@router.get("/printers/{printer_id}/status")
def check_printer_status(printer_id: int) -> Dict[str, Any]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    try:
        adapter = get_adapter(printer["model"], printer.get("config") or {})
        if not isinstance(adapter, DatecsBaseAdapter):
            return {"status": "unknown", "message": "Status check only for Datecs printers"}
        
        from app.transports.factory import create_transport
        from app.datecs_fiscal import (
            _diagnostic_status,
            _SEQ_BY_PRINTER,
            CMD_STATUS,
            _send_with_response,
            _decode_status_flags,
        )
        
        try:
            transport = create_transport(printer)
        except ValueError as exc:
            return {"status": "error", "message": str(exc), "issues": ["config_error"]}
        transport.open()
        try:
            seq = _SEQ_BY_PRINTER.get(printer_id, 0x20)
            timeout_s = int(printer.get("timeout_ms", 5000)) / 1000
            
            seq, status_response = _send_with_response(
                transport, adapter, CMD_STATUS, adapter.data_builder.status_data(), seq, timeout_s, "status", printer_id
            )
            
            status_flags = _decode_status_flags(status_response.status)
            issues = []
            
            if status_flags.get("fiscal_receipt_open") or status_flags.get("service_receipt_open") or status_flags.get("storno_receipt_open"):
                issues.append("receipt_open")
            if status_flags.get("no_paper"):
                issues.append("no_paper")
            if status_flags.get("cover_open"):
                issues.append("cover_open")
            if status_flags.get("clock_not_set"):
                issues.append("clock_not_set")
            
            seq = _diagnostic_status(transport, adapter, seq, timeout_s, printer_id)
            _SEQ_BY_PRINTER[printer_id] = seq
            
            if issues:
                issue_msgs = {
                    "receipt_open": "Отворен бон",
                    "no_paper": "Няма хартия",
                    "cover_open": "Отворен капак",
                    "clock_not_set": "Часовникът не е настроен",
                }
                message = ", ".join([issue_msgs.get(i, i) for i in issues])
                return {"status": "warning", "message": message, "issues": issues}
            
            return {"status": "ok", "message": "Принтерът е готов", "issues": []}
        finally:
            transport.close()
    except Exception as e:
        error_msg = str(e)
        issues = []
        if "no paper" in error_msg.lower() or "хартия" in error_msg.lower():
            issues.append("no_paper")
        if "cover" in error_msg.lower() or "капак" in error_msg.lower():
            issues.append("cover_open")
        if "connection" in error_msg.lower() or "serial" in error_msg.lower():
            issues.append("connection_error")
        if "отворен" in error_msg.lower() or "open" in error_msg.lower():
            issues.append("receipt_open")
        
        return {
            "status": "error",
            "message": error_msg[:200],
            "issues": issues if issues else ["unknown_error"]
        }


@router.get("/printers/{printer_id}/datetime")
def read_printer_datetime(printer_id: int) -> Dict[str, Any]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")

    try:
        adapter = get_adapter(printer["model"], printer.get("config") or {})
        if not isinstance(adapter, DatecsBaseAdapter):
            raise HTTPException(status_code=400, detail="Only Datecs printers support time sync")

        from app.transports.factory import create_transport as _create_transport
        from app.datecs_fiscal import _SEQ_BY_PRINTER, _read_printer_datetime

        transport = _create_transport(printer)
        transport.open()
        try:
            seq = _SEQ_BY_PRINTER.get(printer_id, 0x20)
            timeout_s = int(printer.get("timeout_ms", 5000)) / 1000
            seq, raw, parsed = _read_printer_datetime(
                transport,
                adapter,
                seq,
                timeout_s,
                printer_id,
            )
            _SEQ_BY_PRINTER[printer_id] = seq
            host_now = datetime.now()
            delta_seconds = int((host_now - parsed).total_seconds()) if parsed else None
            return {
                "printer_time": raw,
                "printer_time_iso": parsed.isoformat() if parsed else None,
                "host_time": host_now.strftime("%d-%m-%y %H:%M:%S"),
                "host_time_iso": host_now.isoformat(),
                "delta_seconds": delta_seconds,
            }
        finally:
            transport.close()
    except HTTPException:
        raise
    except Exception as e:
        log_error("DATECS_READ_DATETIME_FAILED", {"printer_id": printer_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to read printer date/time: {str(e)}")


@router.post("/printers/{printer_id}/datetime/sync")
def sync_printer_datetime(printer_id: int, payload: Dict[str, Any] | None = Body(default=None)) -> Dict[str, Any]:
    printer = get_printer(printer_id)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")

    payload = payload or {}
    value = payload.get("datetime") or payload.get("value") or payload.get("time")

    try:
        adapter = get_adapter(printer["model"], printer.get("config") or {})
        if not isinstance(adapter, DatecsBaseAdapter):
            raise HTTPException(status_code=400, detail="Only Datecs printers support time sync")

        from app.transports.factory import create_transport as _ct
        from app.datecs_fiscal import _SEQ_BY_PRINTER, _parse_printer_datetime, _set_printer_datetime

        if value:
            parsed = None
            if isinstance(value, str):
                text = value.strip()
                try:
                    parsed = datetime.fromisoformat(text.replace("Z", ""))
                except ValueError:
                    parsed = _parse_printer_datetime(text)
            if not parsed:
                raise HTTPException(status_code=400, detail="Invalid datetime format")
            target_time = parsed
        else:
            target_time = datetime.now()

        transport = _ct(printer)
        transport.open()
        try:
            seq = _SEQ_BY_PRINTER.get(printer_id, 0x20)
            timeout_s = int(printer.get("timeout_ms", 5000)) / 1000
            seq = _set_printer_datetime(
                transport,
                adapter,
                seq,
                timeout_s,
                printer_id,
                target_time,
            )
            _SEQ_BY_PRINTER[printer_id] = seq
            return {
                "status": "ok",
                "set_time": target_time.strftime("%d-%m-%y %H:%M:%S"),
            }
        finally:
            transport.close()
    except HTTPException:
        raise
    except Exception as e:
        log_error("DATECS_SYNC_DATETIME_FAILED", {"printer_id": printer_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to sync printer date/time: {str(e)}")


@router.get("/tools/models")
def supported_models() -> Dict[str, Any]:
    return {"models": list_supported_models()}


@router.get("/mqtt/status")
def mqtt_status() -> Dict[str, Any]:
    from app.mqtt_client import mqtt_bridge
    return mqtt_bridge.get_status()


@router.get("/mqtt/messages")
def mqtt_messages(limit: int = Query(default=50, le=50)) -> List[Dict[str, Any]]:
    from app.mqtt_client import mqtt_bridge
    return mqtt_bridge.get_messages(limit)


@router.post("/mqtt/publish")
async def mqtt_publish(body: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    from app.mqtt_client import mqtt_bridge
    topic = body.get("topic", "").strip()
    payload = body.get("payload", {})
    qos = int(body.get("qos", 1))
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    ok = await mqtt_bridge.publish(topic, payload, qos=qos)
    return {"ok": ok, "topic": topic}
