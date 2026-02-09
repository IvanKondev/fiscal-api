"""
MQTT client for FiscalAPI.

Subscribes to fiscal topics on an EMQX (or any MQTT 5 / 3.1.1) broker,
creates print jobs from incoming messages, and publishes results back.

Topic structure (configurable via MQTT_TOPIC_PREFIX, default "fiscal"):

    Inbound  (POS → FiscalAPI):
        {prefix}/{printer_id}/receipt   – fiscal receipt
        {prefix}/{printer_id}/storno    – storno receipt
        {prefix}/{printer_id}/report    – Z/X report
        {prefix}/{printer_id}/cancel    – cancel open receipt

    Outbound (FiscalAPI → POS):
        {prefix}/{printer_id}/result    – job result / acknowledgment
        {prefix}/status                 – gateway online/offline (LWT)

Message format (JSON):
    Inbound:  { "request_id": "...", "operator": {...}, "items": [...], "payments": [...], ... }
    Outbound: { "request_id": "...", "status": "success|failed", "receipt_number": "...", "error": null }
"""
from __future__ import annotations

import json
import logging
import ssl
import threading
import time
from typing import Any, Callable, Dict, Optional

from app.app_logging import log_error, log_info
from app.settings import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_CLIENT_ID,
    MQTT_ENABLED,
    MQTT_KEEPALIVE,
    MQTT_PASSWORD,
    MQTT_QOS,
    MQTT_TOPIC_PREFIX,
    MQTT_USE_TLS,
    MQTT_USERNAME,
)

logger = logging.getLogger("mqtt")

# ── Topic helpers ─────────────────────────────────────────────────

PAYLOAD_TYPE_MAP = {
    "receipt": "fiscal_receipt",
    "storno": "storno_receipt",
    "report": "report",
    "cancel": "cancel_receipt",
}


def _topic(suffix: str) -> str:
    return f"{MQTT_TOPIC_PREFIX}/{suffix}"


def _subscribe_pattern() -> str:
    """Wildcard topic: fiscal/+/+  (matches fiscal/{printer_id}/{action})."""
    return f"{MQTT_TOPIC_PREFIX}/+/+"


def _result_topic(printer_id: int | str) -> str:
    return _topic(f"{printer_id}/result")


def _status_topic() -> str:
    return _topic("status")


# ── MQTT Client wrapper ──────────────────────────────────────────

class MqttBridge:
    """Bridges MQTT messages to the FiscalAPI job queue."""

    def __init__(self) -> None:
        self._client: Any = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._connected = False
        self._create_job_fn: Optional[Callable] = None
        self._get_job_fn: Optional[Callable] = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def enabled(self) -> bool:
        return MQTT_ENABLED and bool(MQTT_BROKER_HOST)

    def start(self, create_job_fn: Callable, get_job_fn: Callable) -> None:
        """Start the MQTT bridge in a background thread."""
        if not self.enabled:
            log_info("MQTT_DISABLED", {"reason": "MQTT_ENABLED=false or MQTT_BROKER_HOST empty"})
            return

        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            log_error("MQTT_IMPORT_ERROR", {"error": "paho-mqtt not installed. Run: pip install paho-mqtt>=2.0.0"})
            return

        self._create_job_fn = create_job_fn
        self._get_job_fn = get_job_fn
        self._running = True

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID,
            protocol=mqtt.MQTTv5,
        )

        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        if MQTT_USE_TLS:
            client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        # Last Will and Testament — notify broker we went offline
        lwt_payload = json.dumps({"status": "offline", "client_id": MQTT_CLIENT_ID})
        client.will_set(_status_topic(), lwt_payload, qos=1, retain=True)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        self._client = client
        self._thread = threading.Thread(target=self._loop, daemon=True, name="mqtt-bridge")
        self._thread.start()
        log_info("MQTT_STARTING", {
            "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}",
            "client_id": MQTT_CLIENT_ID,
            "topic_prefix": MQTT_TOPIC_PREFIX,
        })

    def stop(self) -> None:
        """Gracefully disconnect and stop the MQTT loop."""
        self._running = False
        if self._client:
            try:
                online_payload = json.dumps({"status": "offline", "client_id": MQTT_CLIENT_ID})
                self._client.publish(_status_topic(), online_payload, qos=1, retain=True)
                self._client.disconnect()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._connected = False
        log_info("MQTT_STOPPED", {})

    def publish_result(self, printer_id: int, payload: Dict[str, Any]) -> None:
        """Publish a job result back to the broker."""
        if not self._client or not self._connected:
            return
        topic = _result_topic(printer_id)
        try:
            msg = json.dumps(payload, ensure_ascii=False)
            self._client.publish(topic, msg, qos=MQTT_QOS)
            log_info("MQTT_PUBLISH", {"topic": topic, "request_id": payload.get("request_id")})
        except Exception as exc:
            log_error("MQTT_PUBLISH_ERROR", {"topic": topic, "error": str(exc)})

    def get_status(self) -> Dict[str, Any]:
        """Return current MQTT bridge status for the API/UI."""
        return {
            "enabled": self.enabled,
            "connected": self._connected,
            "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}" if self.enabled else None,
            "client_id": MQTT_CLIENT_ID,
            "topic_prefix": MQTT_TOPIC_PREFIX,
        }

    # ── Internal ──────────────────────────────────────────────────

    def _loop(self) -> None:
        """Background thread: connect with retry, then run the network loop."""
        while self._running:
            try:
                self._client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=MQTT_KEEPALIVE)
                self._client.loop_forever()
            except Exception as exc:
                log_error("MQTT_CONNECTION_ERROR", {"error": str(exc)})
                self._connected = False
            if self._running:
                log_info("MQTT_RECONNECTING", {"wait_seconds": 5})
                time.sleep(5)

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: Any, properties: Any = None) -> None:
        self._connected = True
        pattern = _subscribe_pattern()
        client.subscribe(pattern, qos=MQTT_QOS)
        log_info("MQTT_CONNECTED", {"broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}", "subscribed": pattern})

        # Announce online
        online_payload = json.dumps({"status": "online", "client_id": MQTT_CLIENT_ID})
        client.publish(_status_topic(), online_payload, qos=1, retain=True)

    def _on_disconnect(self, client: Any, userdata: Any, flags: Any = None, rc: Any = None, properties: Any = None) -> None:
        self._connected = False
        if self._running:
            log_info("MQTT_DISCONNECTED", {"rc": rc})

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        """Handle an incoming MQTT message by creating a print job."""
        try:
            topic_parts = msg.topic.split("/")
            # Expected: {prefix}/{printer_id}/{action}
            if len(topic_parts) < 3:
                log_error("MQTT_BAD_TOPIC", {"topic": msg.topic})
                return

            printer_id_str = topic_parts[-2]
            action = topic_parts[-1]

            # Skip result topics (our own publishes)
            if action == "result" or action == "status":
                return

            payload_type = PAYLOAD_TYPE_MAP.get(action)
            if not payload_type:
                log_error("MQTT_UNKNOWN_ACTION", {"topic": msg.topic, "action": action})
                return

            try:
                printer_id = int(printer_id_str)
            except ValueError:
                log_error("MQTT_BAD_PRINTER_ID", {"topic": msg.topic, "printer_id": printer_id_str})
                return

            try:
                payload = json.loads(msg.payload.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                log_error("MQTT_BAD_PAYLOAD", {"topic": msg.topic, "error": str(exc)})
                return

            request_id = payload.pop("request_id", None)

            log_info("MQTT_MESSAGE", {
                "topic": msg.topic,
                "printer_id": printer_id,
                "action": action,
                "payload_type": payload_type,
                "request_id": request_id,
            })

            # Create a job through the same pipeline as the REST API
            if self._create_job_fn:
                job = self._create_job_fn(printer_id, payload_type, payload)
                job_id = job["id"]
                log_info("MQTT_JOB_CREATED", {"job_id": job_id, "request_id": request_id})

                # Start a watcher thread to publish the result when the job completes
                if request_id:
                    threading.Thread(
                        target=self._watch_job,
                        args=(printer_id, job_id, request_id),
                        daemon=True,
                        name=f"mqtt-watch-{job_id}",
                    ).start()

        except Exception as exc:
            log_error("MQTT_MESSAGE_ERROR", {"topic": msg.topic, "error": str(exc)})

    def _watch_job(self, printer_id: int, job_id: int, request_id: str) -> None:
        """Poll until a job finishes, then publish the result via MQTT."""
        if not self._get_job_fn:
            return
        for _ in range(60):  # max ~30 seconds
            time.sleep(0.5)
            try:
                job = self._get_job_fn(job_id)
                if not job:
                    break
                status = job.get("status", "")
                if status in ("success", "failed"):
                    result_payload: Dict[str, Any] = {
                        "request_id": request_id,
                        "job_id": job_id,
                        "status": status,
                        "error": job.get("error"),
                    }
                    if status == "success" and job.get("result"):
                        result_payload.update({
                            "receipt_number": job["result"].get("receipt_number"),
                            "total_amount": job["result"].get("total_amount"),
                        })
                    self.publish_result(printer_id, result_payload)
                    return
            except Exception as exc:
                log_error("MQTT_WATCH_ERROR", {"job_id": job_id, "error": str(exc)})
                break
        # Timeout
        self.publish_result(printer_id, {
            "request_id": request_id,
            "job_id": job_id,
            "status": "failed",
            "error": "Job timed out waiting for result",
        })


# ── Singleton ─────────────────────────────────────────────────────

mqtt_bridge = MqttBridge()
