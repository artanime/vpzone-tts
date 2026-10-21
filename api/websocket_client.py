import json
import re
import threading
import time

import websocket

from core.logger_manager import LoggerManager

# Claves donde el servidor puede traer el texto del mensaje.
# VPZone usa "body"; el resto son compatibilidad con otros formatos.
TEXT_KEYS = ("body", "message", "text", "content")

# Tipos de frame que representan un mensaje de chat con texto (VPZone).
CHAT_TYPES = {"msg", "message", "chat"}

# Un slug de canal válido según la API de VPZone.
CHANNEL_PATTERN = re.compile(r"^[a-z0-9_-]{3,32}$")

# Margen (ms) para descartar el historial que reenvía el servidor al conectar.
# Todo frame anterior a "ahora - margen" se considera historia y se ignora.
HISTORY_TOLERANCE_MS = 2000

FRIENDLY_INVALID_CHANNEL = (
    "Canal inválido o sin permiso (código 1008). Usa el slug del canal en "
    "minúsculas (solo a-z, 0-9, \"_\" o \"-\"; 3-32 caracteres)."
)


def normalize_channel(value):
    """Devuelve el canal normalizado (minúsculas, sin espacios)."""

    if value is None:
        return ""

    return str(value).strip().lower()


def valid_channel(slug):
    """Comprueba si el slug cumple el patrón de la API de VPZone."""

    return bool(CHANNEL_PATTERN.match(slug or ""))


def extract_chat(data):
    """Normaliza un frame crudo del chat de VPZone a un dict tipado."""

    if not isinstance(data, dict):
        return None

    # Algunos servidores envuelven el payload en "data".
    payload = data.get("data")

    if not isinstance(payload, dict):
        payload = data

    # VPZone: solo los frames de tipo mensaje contienen texto para TTS.
    # (se ignoran presence, delete_message, pin_update, error, etc.)
    kind = payload.get("type")

    if isinstance(kind, str) and kind.lower() not in CHAT_TYPES:
        return None

    text = None

    for key in TEXT_KEYS:

        value = payload.get(key)

        if isinstance(value, str) and value.strip():
            text = value.strip()
            break

    if text is None:
        return None

    # Autor: cadena plana (VPZone), dict anidado o campos sueltos.
    author = payload.get("author") or payload.get("user")

    username = ""
    display_name = ""
    role = ""
    priority = None

    if isinstance(author, str):

        username = author

    elif isinstance(author, dict):

        username = author.get("username") or author.get("name") or ""
        display_name = author.get("display_name") or author.get("name") or ""
        role = author.get("role") or author.get("level") or ""

        if isinstance(author.get("priority"), int):
            priority = author["priority"]

    username = payload.get("username") or payload.get("nick") or username
    display_name = payload.get("display_name") or display_name
    role = role or payload.get("role") or ""

    # Rol/prioridad derivados de los flags de VPZone.
    if not role:

        if payload.get("is_owner"):
            role = "owner"
        elif payload.get("is_mod"):
            role = "moderator"
        elif payload.get("is_subscriber"):
            role = "subscriber"
        else:
            role = "viewer"

    if priority is None:

        if isinstance(payload.get("priority"), int):
            priority = payload["priority"]
        elif role in ("admin", "moderator", "owner"):
            priority = 100
        elif role == "subscriber":
            priority = 10
        else:
            priority = 0

    return {
        "text": text,
        "username": username or "",
        "display_name": display_name or "",
        "role": role or "viewer",
        "language": payload.get("language", "auto"),
        "priority": priority,
        "channel": payload.get("channel", "")
    }


class WebSocketClient(threading.Thread):

    def __init__(self, event_manager, channel, url="wss://chat.vpzone.tv/ws",
                 channel_param="channel", skip_history=True):

        super().__init__(name="WebSocketClient", daemon=True)

        self.events = event_manager
        self.channel = normalize_channel(channel)
        self.base_url = url
        self.channel_param = channel_param
        self.skip_history = skip_history

        # Marca de tiempo (ms) por debajo de la cual se ignora el historial.
        self._history_cutoff = None

        self.ws = None

        self.running = False

        self.backoff = 1

    @property
    def connected(self):

        return self.ws is not None and self.running

    def build_url(self):

        params = [f"{self.channel_param}={self.channel}"]

        # Pedimos al servidor solo lo que pasa a partir de ahora: así no
        # reenvía el historial antiguo al abrir/reabrir la aplicación.
        if self.skip_history:
            params.append(f"since={int(time.time() * 1000)}")

        separator = "&" if "?" in self.base_url else "?"

        return f"{self.base_url}{separator}{'&'.join(params)}"

    def connect(self):

        url = self.build_url()

        LoggerManager.logger.info(f"Conectando al chat: {url}")

        self.ws = websocket.WebSocketApp(

            url,

            on_open=self.on_open,

            on_message=self.on_message,

            on_error=self.on_error,

            on_close=self.on_close

        )

        self.ws.run_forever(
            ping_interval=30,
            ping_timeout=10
        )

    def run(self):

        self.running = True

        if not valid_channel(self.channel):

            LoggerManager.logger.error(FRIENDLY_INVALID_CHANNEL)

            self.events.emit(
                "connection.error",
                {"error": FRIENDLY_INVALID_CHANNEL, "code": 1008}
            )

            self.running = False

            return

        while self.running:

            try:

                self.connect()

            except Exception as exc:

                LoggerManager.logger.error(f"WebSocket: {exc}")

                self.events.emit(
                    "connection.error",
                    {"error": str(exc)}
                )

            if not self.running:
                break

            self.events.emit("connection.closed", {})

            delay = self.backoff

            while self.running and delay > 0:

                time.sleep(1)

                delay -= 1

            self.backoff = min(self.backoff * 2, 60)

    def stop(self):

        self.running = False

        ws = self.ws

        if ws is not None:

            try:
                ws.close()
            except Exception:
                pass

        LoggerManager.logger.info("WebSocket detenido")

    def on_open(self, ws):

        self.backoff = 1

        # Al conectar (o reconectar) fijamos el corte: todo lo anterior es
        # historial que el servidor reenvía y no debe leerse.
        if self.skip_history:
            self._history_cutoff = int(time.time() * 1000) - HISTORY_TOLERANCE_MS
        else:
            self._history_cutoff = None

        LoggerManager.logger.info("WebSocket conectado")

        print("[WS] Conectado al chat")

        self.events.emit("connection.open", {"channel": self.channel})

    def on_close(self, ws, code, msg):

        if code == 1008:

            LoggerManager.logger.error(FRIENDLY_INVALID_CHANNEL)

            self.running = False

            self.events.emit(
                "connection.error",
                {"error": FRIENDLY_INVALID_CHANNEL, "code": 1008}
            )

        else:

            LoggerManager.logger.warning(f"WebSocket cerrado (código {code})")

        print(f"[WS] Desconectado (código {code})")

    def on_error(self, ws, error):

        text = str(error)

        if "1008" in text or "bad channel" in text.lower():

            LoggerManager.logger.error(FRIENDLY_INVALID_CHANNEL)

            self.running = False

            self.events.emit(
                "connection.error",
                {"error": FRIENDLY_INVALID_CHANNEL, "code": 1008}
            )

            return

        LoggerManager.logger.error(f"WebSocket error: {error}")

        self.events.emit("connection.error", {"error": text})

    def on_message(self, ws, message):

        try:

            data = json.loads(message)

        except json.JSONDecodeError:

            LoggerManager.logger.warning(f"Mensaje no JSON ignorado: {message[:80]}")

            return

        # Descartar el historial que el servidor reenvía al conectar.
        if self._history_cutoff is not None and isinstance(data, dict):

            ts = data.get("ts")

            if isinstance(ts, int) and ts < self._history_cutoff:
                return

        self.events.emit("websocket.message", data)

        chat = extract_chat(data)

        if chat:

            self.events.emit("chat.message", chat)
