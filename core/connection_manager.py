from api.websocket_client import (
    FRIENDLY_INVALID_CHANNEL,
    WebSocketClient,
    normalize_channel,
    valid_channel
)
from api.woupi.eventsub import WoupiWebSocketClient
from api.woupi.rest import WoupiError, WoupiRestClient
from core.logger_manager import LoggerManager


DEFAULT_WOUPI_API = "https://api.woupi.buzz"
DEFAULT_WOUPI_WSS = "wss://api.woupi.buzz/eventsub"


class ConnectionManager:

    def __init__(self, event_manager, config):

        self.events = event_manager
        self.config = config

        self.websocket = None

    @property
    def connected(self):

        return self.websocket is not None and self.websocket.running

    @property
    def channel(self):

        return self.config.get("channel", "")

    @property
    def platform(self):

        return (self.config.get("platform") or "vpzone").strip().lower()

    def start(self):

        if self.platform == "woupi":
            return self._start_woupi()

        return self._start_vpzone()

    def restart(self):

        self.stop()

        return self.start()

    def stop(self):

        websocket = self.websocket

        self.websocket = None

        if websocket is None:
            return

        websocket.stop()

        if websocket.is_alive():

            websocket.join(timeout=5)

        LoggerManager.logger.info("ConnectionManager detenido")

    # ------------------------------------------------------------------ #
    # VPZone

    def _start_vpzone(self):

        channel = normalize_channel(self.channel)

        if not channel:

            LoggerManager.logger.warning("No hay un canal configurado.")

            print("[Conexión] No hay un canal configurado en config.json")

            self.events.emit(
                "connection.missing_channel",
                {"channel": ""}
            )

            return False

        if not valid_channel(channel):

            LoggerManager.logger.error(FRIENDLY_INVALID_CHANNEL)

            print(f"[Conexión] {FRIENDLY_INVALID_CHANNEL}")

            self.events.emit(
                "connection.error",
                {"error": FRIENDLY_INVALID_CHANNEL, "code": 1008}
            )

            return False

        self.websocket = WebSocketClient(
            self.events,
            channel,
            url=self.config.get(
                "websocket_url",
                "wss://chat.vpzone.tv/ws"
            ),
            channel_param=self.config.get("websocket_param", "channel"),
            skip_history=self.config.get("tts.skip_history", True)
        )

        self.websocket.start()

        LoggerManager.logger.info("ConnectionManager iniciado")

        return True

    # ------------------------------------------------------------------ #
    # Woupi

    def _start_woupi(self):

        client_id = (self.config.get("woupi.client_id") or "").strip()
        access_token = (self.config.get("woupi.access_token") or "").strip()
        refresh_token = (self.config.get("woupi.refresh_token") or "").strip()

        if not client_id or not access_token:

            message = (
                "Faltan credenciales de Woupi: define 'woupi.client_id' en "
                "config.json y el access_token en .env, o autoriza con el "
                "boton 'Cuenta Woupi'."
            )

            LoggerManager.logger.error(message)

            self.events.emit("connection.error", {"error": message})

            return False

        channel = normalize_channel(self.channel)

        if not channel:

            LoggerManager.logger.warning("No hay un canal configurado.")

            self.events.emit("connection.missing_channel", {"channel": ""})

            return False

        rest = WoupiRestClient(
            client_id=client_id,
            access_token=access_token,
            refresh_token=refresh_token,
            base_url=self.config.get("woupi.api_base_url", DEFAULT_WOUPI_API)
        )

        # Guardar los tokens renovados para no volver a autorizar.
        rest.on_tokens_refreshed = self._persist_woupi_tokens

        user_id = (self.config.get("woupi.user_id") or "").strip()

        if not user_id:

            info = rest.validate()

            user_id = str((info or {}).get("user_id") or "").strip()

        if not user_id:

            message = (
                "No se pudo determinar el usuario del token de Woupi "
                "(revisa 'woupi.user_id' o el access token)."
            )

            LoggerManager.logger.error(message)

            self.events.emit("connection.error", {"error": message})

            return False

        broadcaster_id = (self.config.get("woupi.broadcaster_id") or "").strip()

        if not broadcaster_id:

            try:

                user = rest.get_user_by_login(channel)

            except WoupiError as exc:

                LoggerManager.logger.error(f"Woupi: {exc}")

                self.events.emit("connection.error", {"error": str(exc)})

                return False

            broadcaster_id = str((user or {}).get("id") or "").strip()

        if not broadcaster_id:

            message = f"Canal de Woupi no encontrado: {channel}"

            LoggerManager.logger.error(message)

            self.events.emit("connection.error", {"error": message})

            return False

        self.websocket = WoupiWebSocketClient(
            self.events,
            rest,
            broadcaster_id=broadcaster_id,
            user_id=user_id,
            channel=channel,
            url=self.config.get("woupi.eventsub_url", DEFAULT_WOUPI_WSS),
            ignore_own_messages=self.config.get(
                "woupi.ignore_own_messages", False
            )
        )

        self.websocket.start()

        LoggerManager.logger.info("ConnectionManager (Woupi) iniciado")

        return True

    def _persist_woupi_tokens(self, access_token, refresh_token):

        if access_token:
            self.config.set("woupi.access_token", access_token)

        if refresh_token:
            self.config.set("woupi.refresh_token", refresh_token)

        self.config.save()
