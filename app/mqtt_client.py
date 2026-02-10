"""
MQTT client for FiscalAPI — powered by aiomqtt (async).

Connects to EMQX broker over WebSocket, subscribes to configured topics,
logs all incoming messages. Ready to be extended with job creation
once the topic structure and message format are agreed upon.
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.app_logging import log_error, log_info
from app.settings import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_CLIENT_ID,
    MQTT_ENABLED,
    MQTT_KEEPALIVE,
    MQTT_PASSWORD,
    MQTT_TOPIC_SUBSCRIBE,
    MQTT_TRANSPORT,
    MQTT_USERNAME,
    MQTT_WS_PATH,
)

logger = logging.getLogger("mqtt")


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

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def enabled(self) -> bool:
        return MQTT_ENABLED and bool(MQTT_BROKER_HOST)

    def start(self) -> None:
        """Start the MQTT listener as an asyncio background task."""
        if not self.enabled:
            log_info("MQTT_DISABLED", {
                "reason": "MQTT_ENABLED=false or MQTT_BROKER_HOST empty",
            })
            return
        self._task = asyncio.create_task(self._run())
        log_info("MQTT_STARTING", {
            "broker": f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}",
            "transport": MQTT_TRANSPORT,
            "client_id": MQTT_CLIENT_ID,
            "topic": MQTT_TOPIC_SUBSCRIBE,
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
            "topic": MQTT_TOPIC_SUBSCRIBE,
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
                        "topic": MQTT_TOPIC_SUBSCRIBE,
                    })

                    await client.subscribe(MQTT_TOPIC_SUBSCRIBE)

                    async for message in client.messages:
                        self._on_message(message)

            except asyncio.CancelledError:
                log_info("MQTT_CANCELLED", {})
                self._connected = False
                return
            except Exception as exc:
                self._connected = False
                log_error("MQTT_CONNECTION_ERROR", {"error": str(exc)})
                log_info("MQTT_RECONNECTING", {"wait_seconds": 5})
                await asyncio.sleep(5)

    def _on_message(self, message: Any) -> None:
        """Handle an incoming MQTT message — log it for now."""
        topic = str(message.topic)
        try:
            payload_raw = message.payload.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            payload_raw = str(message.payload)

        # Try to parse as JSON
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

        # ── TODO: Route message to job queue when format is agreed ──
        # Example future flow:
        #   printer_id = extract_printer_id(topic)
        #   job = create_job(printer_id, payload_type, payload_parsed)


# ── Singleton ─────────────────────────────────────────────────────
mqtt_bridge = MqttBridge()
