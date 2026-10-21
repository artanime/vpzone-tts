"""Cliente WebSocket (EventSub) del chat de Woupi.

A diferencia de VPZone, Woupi no entrega el chat por un WebSocket directo:
hay que abrir ``wss://api.woupi.buzz/eventsub``, esperar el mensaje
``session_welcome`` y, en los primeros 10 segundos, crear una suscripción
``channel.chat.message`` vía REST con el ``session_id`` recibido.

Este cliente hace todo eso y traduce cada notificación al mismo formato que
usa el resto de la app para el TTS::

    {"text", "username", "display_name", "role", "language",
     "priority", "channel"}

Además detecta conexiones muertas (watchdog) y reconecta con backoff.
"""

import json
import threading
import time

import websocket

from api.woupi.rest import WoupiError
from core.logger_manager import LoggerManager


DEFAULT_URL = "wss://api.woupi.buzz/eventsub"

# Margen (ms) sobre keepalive_timeout_seconds para detectar conexión muerta.
KEEPALIVE_MARGIN_MS = 5000

# Tiempo máximo (ms) que esperamos el primer mensaje tras conectar.
WELCOME_TIMEOUT_MS = 10000


def extract_chat(event, broadcaster_id, user_id, channel="", ignore_own=False):
    """Normaliza el ``event`` de ``channel.chat.message`` al formato del TTS."""

    if not isinstance(event, dict):
        return None

    message = event.get("message")

    if isinstance(message, dict):
        text = message.get("text")
    else:
        text = message

    if not isinstance(text, str) or not text.strip():
        return None

    chatter_id = str(event.get("chatter_user_id") or "")

    # Opcional: ignorar los mensajes del propio bot (evita bucles si responde).
    if ignore_own and user_id and chatter_id and chatter_id == str(user_id):
        return None

    owner = bool(broadcaster_id) and chatter_id == str(broadcaster_id)

    return {
        "text": text.strip(),
        "username": event.get("chatter_user_login") or "",
        "display_name": event.get("chatter_user_name") or "",
        "role": "owner" if owner else "viewer",
        "language": "auto",
        "priority": 100 if owner else 0,
        "channel": channel
    }


class WoupiWebSocketClient(threading.Thread):
    """Lee el chat de un canal de Woupi a través de EventSub."""

    def __init__(self, event_manager, rest, broadcaster_id, user_id,
                 channel="", url=DEFAULT_URL, reconnect_delay=5,
                 ignore_own_messages=False):

        super().__init__(name="WoupiWebSocketClient", daemon=True)

        self.events = event_manager
        self.rest = rest
        self.broadcaster_id = str(broadcaster_id)
        self.user_id = str(user_id)
        self.channel = channel
        self.base_url = url or DEFAULT_URL
        self.reconnect_delay = max(1, int(reconnect_delay))
        self.ignore_own_messages = bool(ignore_own_messages)

        self.running = False
        self.ws = None
        self.session_id = None
        self.subscribed = False

        self.backoff = self.reconnect_delay

        self._timeout_ms = WELCOME_TIMEOUT_MS + KEEPALIVE_MARGIN_MS
        self._watchdog = None

    @property
    def connected(self):

        return self.ws is not None and self.running and self.subscribed

    # ------------------------------------------------------------------ #

    def run(self):

        self.running = True

        while self.running:

            try:

                self.connect()

            except Exception as exc:

                LoggerManager.logger.error(f"Woupi WebSocket: {exc}")

                self.events.emit("connection.error", {"error": str(exc)})

            if not self.running:
                break

            self.events.emit("connection.closed", {})

            self._sleep_backoff()

        self.running = False

    def _sleep_backoff(self):

        delay = self.backoff

        while self.running and delay > 0:

            time.sleep(1)

            delay -= 1

        self.backoff = min(self.backoff * 2, 60)

    def connect(self):

        LoggerManager.logger.info(
            f"Conectando al EventSub de Woupi: {self.base_url}"
        )

        self.ws = websocket.WebSocketApp(

            self.base_url,

            on_open=self.on_open,

            on_message=self.on_message,

            on_error=self.on_error,

            on_close=self.on_close

        )

        # No enviamos pings de cliente: el servidor manda keepalives cada 10s
        # y cualquier tráfico entrante cierra la conexión con el código 4001.
        self.ws.run_forever(ping_interval=0)

    def stop(self):

        self.running = False

        self._cancel_watchdog()

        ws = self.ws

        if ws is not None:

            try:
                ws.close()
            except Exception:
                pass

        LoggerManager.logger.info("Woupi WebSocket detenido")

    # ------------------------------------------------------------------ #
    # Callbacks de websocket-client

    def on_open(self, ws):

        self.backoff = self.reconnect_delay
        self.subscribed = False

        LoggerManager.logger.info("Woupi WebSocket conectado (esperando welcome)")

        # El servidor debe mandar el welcome; si no, reconectamos.
        self._timeout_ms = WELCOME_TIMEOUT_MS + KEEPALIVE_MARGIN_MS
        self._arm_watchdog()

    def on_message(self, ws, message):

        self._arm_watchdog()

        try:

            data = json.loads(message)

        except json.JSONDecodeError:

            LoggerManager.logger.warning("Woupi: mensaje no JSON ignorado")

            return

        self.events.emit("websocket.message", data)

        metadata = data.get("metadata") or {}
        payload = data.get("payload") or {}

        kind = metadata.get("message_type")

        if kind == "session_welcome":

            session = payload.get("session") or {}

            self.session_id = session.get("id")

            timeout_s = session.get("keepalive_timeout_seconds") or 10

            self._timeout_ms = int(timeout_s) * 1000 + KEEPALIVE_MARGIN_MS

            self._arm_watchdog()

            self.subscribe()

        elif kind == "notification":

            self.handle_notification(metadata, payload)

    def on_error(self, ws, error):

        LoggerManager.logger.error(f"Woupi WebSocket error: {error}")

        if self.running:

            self.events.emit("connection.error", {"error": str(error)})

    def on_close(self, ws, code, msg):

        self._cancel_watchdog()

        self.subscribed = False

        if not self.running:
            return

        LoggerManager.logger.warning(
            f"Woupi WebSocket cerrado (código {code})"
        )

    # ------------------------------------------------------------------ #
    # Suscripción y eventos

    def subscribe(self):

        if not self.session_id:
            return

        try:

            self.rest.create_eventsub_subscription(
                event_type="channel.chat.message",
                version="1",
                condition={
                    "broadcaster_user_id": self.broadcaster_id,
                    "user_id": self.user_id
                },
                transport={
                    "method": "websocket",
                    "session_id": self.session_id
                }
            )

        except WoupiError as exc:

            LoggerManager.logger.error(f"Woupi: suscripción fallida: {exc}")

            self.events.emit("connection.error", {
                "error": f"No se pudo suscribir al chat de Woupi: {exc}"
            })

            self.subscribed = False

            self._close()

            return

        self.subscribed = True
        self.backoff = self.reconnect_delay

        LoggerManager.logger.info("Woupi: suscripción al chat activa")

        self.events.emit("connection.open", {"channel": self.channel})

    def handle_notification(self, metadata, payload):

        if metadata.get("subscription_type") != "channel.chat.message":
            return

        chat = extract_chat(
            payload.get("event"),
            self.broadcaster_id,
            self.user_id,
            self.channel,
            ignore_own=self.ignore_own_messages
        )

        if chat:
            self.events.emit("chat.message", chat)

    # ------------------------------------------------------------------ #
    # Watchdog (detección de conexión muerta)

    def _arm_watchdog(self):

        self._cancel_watchdog()

        if not self.running:
            return

        self._watchdog = threading.Timer(
            self._timeout_ms / 1000.0,
            self._on_watchdog
        )

        self._watchdog.daemon = True

        self._watchdog.start()

    def _cancel_watchdog(self):

        timer, self._watchdog = self._watchdog, None

        if timer is not None:

            try:
                timer.cancel()
            except Exception:
                pass

    def _on_watchdog(self):

        if not self.running:
            return

        LoggerManager.logger.warning(
            "Woupi: sin mensajes dentro del plazo, reconectando"
        )

        self._close()

    def _close(self):

        ws = self.ws

        if ws is not None:

            try:
                ws.close()
            except Exception:
                pass
