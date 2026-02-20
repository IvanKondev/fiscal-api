"""
MQTT client for FiscalAPI — powered by aiomqtt (async).

Connects to EMQX broker, subscribes to fiscal/{PRINTER_GUID}/print/#,
creates print jobs from incoming messages, and publishes results back
to fiscal/{PRINTER_GUID}/result.

Topic structure:
  fiscal/{guid}/print/receipt  — BE → FiscalAPI: print fiscal receipt
  fiscal/{guid}/print/report   — BE → FiscalAPI: print Z/X report
  fiscal/{guid}/result         — FiscalAPI → BE: job result (success/error)
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.app_logging import log_error, log_info
from app.db import create_job, get_job, list_printers
from app.settings import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_CLIENT_ID,
    MQTT_ENABLED,
    MQTT_KEEPALIVE,
    MQTT_PASSWORD,
    MQTT_TRANSPORT,
    MQTT_USERNAME,
    MQTT_WS_PATH,
    PRINTER_GUID,
)

logger = logging.getLogger("mqtt")

# Map topic suffix → FiscalAPI payload_type
_TOPIC_TO_PAYLOAD_TYPE = {
    "receipt": "fiscal_receipt",
    "report": "report",
}

# How often to poll for job completion (seconds)
_JOB_POLL_INTERVAL = 1.0
# Max time to wait for a job to finish before giving up (seconds)
_JOB_WAIT_TIMEOUT = 60.0


class MqttBridge:
    """Async MQTT bridge using aiomqtt."""

    MAX_HISTORY = 50

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._client: Any = None
        self._connected = False
        self._message_count = 0
        self._last_message: Optional[Dict[str, Any]] = None
        self._messages: deque[Dict[str, Any]] = deque(maxlen=self.MAX_HISTORY)
        self._printer_id: Optional[int] = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def enabled(self) -> bool:
        return MQTT_ENABLED and bool(MQTT_BROKER_HOST) and bool(PRINTER_GUID)

    @property
    def subscribe_topic(self) -> str:
        return f"fiscal/{PRINTER_GUID}/print/#"

    @property
    def result_topic(self) -> str:
        return f"fiscal/{PRINTER_GUID}/result"

    def _resolve_printer_id(self) -> Optional[int]:
        """Find the first enabled printer to use for MQTT jobs."""
        if self._printer_id is not None:
            return self._printer_id
        printers = list_printers()
        for p in printers:
            if p.get("enabled"):
                self._printer_id = int(p["id"])
                return self._printer_id
        return None

    def start(self) -> None:
        """Start the MQTT listener as an asyncio background task."""
        if not self.enabled:
            reason = []
            if not MQTT_ENABLED:
                reason.append("MQTT_ENABLED=false")
            if not MQTT_BROKER_HOST:
                reason.append("MQTT_BROKER_HOST empty")
            if not PRINTER_GUID:
                reason.append("PRINTER_GUID empty")
            log_info("MQTT_DISABLED", {"reason": ", ".join(reason)})
            return
        self._task = asyncio.create_task(self._run())
        log_info("MQTT_STARTING", {
            "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}",
            "transport": MQTT_TRANSPORT,
            "client_id": MQTT_CLIENT_ID,
            "printer_guid": PRINTER_GUID,
            "subscribe_topic": self.subscribe_topic,
        })

    async def stop(self) -> None:
        """Cancel the background listener."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._client = None
        self._connected = False
        log_info("MQTT_STOPPED", {})

    async def publish(self, topic: str, payload: Any, qos: int = 1) -> bool:
        """Publish a JSON message. Returns True on success."""
        if not self._connected or not self._client:
            log_error("MQTT_PUBLISH_NOT_CONNECTED", {"topic": topic})
            return False
        try:
            msg = json.dumps(payload, ensure_ascii=False, default=str)
            await self._client.publish(topic, msg.encode("utf-8"), qos=qos)
            log_info("MQTT_PUBLISH", {"topic": topic, "payload": payload})
            return True
        except Exception as exc:
            log_error("MQTT_PUBLISH_ERROR", {"topic": topic, "error": str(exc)})
            return False

    def get_status(self) -> Dict[str, Any]:
        """Return MQTT bridge status for the API / UI."""
        return {
            "enabled": self.enabled,
            "connected": self._connected,
            "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}" if self.enabled else None,
            "transport": MQTT_TRANSPORT,
            "client_id": MQTT_CLIENT_ID,
            "printer_guid": PRINTER_GUID,
            "subscribe_topic": self.subscribe_topic if self.enabled else None,
            "result_topic": self.result_topic if self.enabled else None,
            "message_count": self._message_count,
            "last_message": self._last_message,
        }

    def get_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent MQTT messages (newest first)."""
        msgs = list(self._messages)
        msgs.reverse()
        return msgs[:limit]

    # ── Internal ──────────────────────────────────────────────────

    async def _run(self) -> None:
        """Connect with auto-reconnect and listen for messages."""
        import aiomqtt

        while True:
            try:
                async with aiomqtt.Client(
                    hostname=MQTT_BROKER_HOST,
                    port=MQTT_BROKER_PORT,
                    username=MQTT_USERNAME or None,
                    password=MQTT_PASSWORD or None,
                    identifier=MQTT_CLIENT_ID,
                    transport=MQTT_TRANSPORT,
                    websocket_path=MQTT_WS_PATH if MQTT_TRANSPORT == "websockets" else None,
                    keepalive=MQTT_KEEPALIVE,
                    protocol=aiomqtt.ProtocolVersion.V5,
                ) as client:
                    self._client = client
                    self._connected = True
                    log_info("MQTT_CONNECTED", {
                        "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}",
                        "subscribe_topic": self.subscribe_topic,
                    })

                    await client.subscribe(self.subscribe_topic)

                    async for message in client.messages:
                        await self._on_message(message)

            except asyncio.CancelledError:
                log_info("MQTT_CANCELLED", {})
                self._connected = False
                return
            except Exception as exc:
                self._connected = False
                log_error("MQTT_CONNECTION_ERROR", {"error": str(exc)})
                log_info("MQTT_RECONNECTING", {"wait_seconds": 5})
                await asyncio.sleep(5)

    async def _on_message(self, message: Any) -> None:
        """Handle an incoming MQTT message — route to job queue."""
        topic = str(message.topic)
        try:
            payload_raw = message.payload.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            payload_raw = str(message.payload)

        payload_parsed = None
        try:
            payload_parsed = json.loads(payload_raw)
        except (json.JSONDecodeError, ValueError):
            pass

        self._message_count += 1
        entry = {
            "id": self._message_count,
            "topic": topic,
            "payload": payload_parsed if payload_parsed is not None else payload_raw,
            "qos": message.qos,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        self._last_message = entry
        self._messages.append(entry)

        log_info("MQTT_MESSAGE", {
            "topic": topic,
            "payload": payload_parsed if payload_parsed is not None else payload_raw,
            "qos": message.qos,
            "count": self._message_count,
        })

        if not isinstance(payload_parsed, dict):
            log_error("MQTT_INVALID_PAYLOAD", {"topic": topic, "reason": "not a JSON object"})
            return

        # Extract action from topic: fiscal/{guid}/print/{action}
        parts = topic.split("/")
        action = parts[-1] if len(parts) >= 4 else None
        payload_type = _TOPIC_TO_PAYLOAD_TYPE.get(action)
        if not payload_type:
            log_error("MQTT_UNKNOWN_ACTION", {"topic": topic, "action": action})
            return

        request_id = payload_parsed.get("request_id", "")

        printer_id = self._resolve_printer_id()
        if printer_id is None:
            log_error("MQTT_NO_PRINTER", {"topic": topic})
            await self._publish_result(request_id, "failed", error="No enabled printer found")
            return

        # Create job in the queue — the existing JobQueue will pick it up
        try:
            job = create_job(printer_id, payload_type, payload_parsed)
            job_id = int(job["id"])
            log_info("MQTT_JOB_CREATED", {
                "job_id": job_id,
                "printer_id": printer_id,
                "payload_type": payload_type,
                "request_id": request_id,
            })
        except Exception as exc:
            log_error("MQTT_JOB_CREATE_ERROR", {"error": str(exc), "topic": topic})
            await self._publish_result(request_id, "failed", error=str(exc))
            return

        # Wait for job completion in a background task and publish result
        asyncio.create_task(self._wait_and_publish(job_id, request_id))

    async def _wait_and_publish(self, job_id: int, request_id: str) -> None:
        """Poll for job completion, then publish result via MQTT."""
        elapsed = 0.0
        while elapsed < _JOB_WAIT_TIMEOUT:
            await asyncio.sleep(_JOB_POLL_INTERVAL)
            elapsed += _JOB_POLL_INTERVAL
            job = get_job(job_id)
            if not job:
                break
            if job["status"] in ("success", "failed"):
                await self._publish_result(
                    request_id=request_id,
                    status=job["status"],
                    result=job.get("result"),
                    error=job.get("error"),
                )
                return

        # Timeout
        log_error("MQTT_JOB_TIMEOUT", {"job_id": job_id, "request_id": request_id})
        await self._publish_result(
            request_id=request_id,
            status="failed",
            error=f"Job {job_id} timed out after {_JOB_WAIT_TIMEOUT}s",
        )

    async def _publish_result(
        self,
        request_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Publish job result to fiscal/{PRINTER_GUID}/result."""
        payload: Dict[str, Any] = {
            "request_id": request_id,
            "printer_guid": PRINTER_GUID,
            "status": status,
        }
        if result:
            payload["result"] = result
        if error:
            payload["error"] = error
        await self.publish(self.result_topic, payload)


# ── Singleton ─────────────────────────────────────────────────────
mqtt_bridge = MqttBridge()
