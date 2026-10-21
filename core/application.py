import threading

from core.constants import APP_NAME, VERSION
from core.config_manager import ConfigManager
from core.connection_manager import ConnectionManager
from core.event_manager import EventManager
from core.folder_manager import FolderManager
from core.logger_manager import LoggerManager
from core.paths import purge_temp
from core.service_manager import ServiceManager

from tts.filter_registry import FilterRegistry
from tts.provider_factory import ProviderFactory
from tts.service import TTSService

from runtime.core.plugin_service import PluginService

from api.client import VPZoneClient


class Application:

    def __init__(self, headless=False):

        # Carpetas base (logs, temp, plugins...)
        FolderManager.create()

        self.headless = headless

        # Configuración (se carga ANTES de construir los servicios)
        self.config = ConfigManager()
        self.config.load()

        # Sistema de eventos
        self.events = EventManager()

        # Servicios
        self.services = ServiceManager()

        # Conexiones
        self.connection = None
        self.api = None

        # Servicio TTS
        self.tts = TTSService(
            self.config,
            self.events
        )

        self.services.register(self.tts)

        # Plugins
        self.plugins = PluginService(
            config=self.config,
            events=self.events,
            services=self.services,
            providers=ProviderFactory,
            filters=FilterRegistry(self.config)
        )

        self.services.register(self.plugins)

        self.started = False

        self._shutdown = threading.Event()

        self._temp_thread = None

        self.register_events()

    # ------------------------------------------------------------------ #

    def register_events(self):

        self.events.on("chat.message", self.on_chat_message)

        self.events.on("program.started", self.on_program_started)

        self.events.on("tts.rejected", self.on_tts_rejected)

        self.events.on("connection.open", self.on_connection_open)

    def on_connection_open(self, data):
        """Al conectar (o reconectar) vacía la cola para no leer historial."""

        if not self.config.get("tts.skip_history", True):
            return

        if self.tts is None:
            return

        cleared = self.tts.clear_queue()

        LoggerManager.logger.info(
            f"Chat conectado: cola vaciada ({cleared} mensajes en espera)"
        )

    def on_program_started(self, data):

        LoggerManager.logger.info(
            f"{APP_NAME} v{VERSION} listo (canal: {self.config.get('channel')})"
        )

    def on_tts_rejected(self, data):

        message = (data or {}).get("message") or {}

        LoggerManager.logger.info(
            f"Mensaje filtrado por {data.get('reason')}: "
            f"{message.get('text', '')!r}"
        )

    def on_chat_message(self, data):
        """Convierte un mensaje del chat en un evento TTS."""

        if not isinstance(data, dict):
            return

        text = (data.get("text") or "").strip()

        if not text:
            return

        if self.config.get("tts.read_username", False):

            name = data.get("display_name") or data.get("username")

            if name:
                text = f"{name} dice: {text}"

        payload = {
            "text": text,
            "username": data.get("username", ""),
            "display_name": data.get("display_name", ""),
            "role": data.get("role", "viewer"),
            "language": data.get("language", "auto"),
            "priority": data.get("priority", 0),
            "channel": data.get("channel", "")
        }

        self.events.emit("tts.speak", payload)

    # ------------------------------------------------------------------ #

    def start(self):

        if self.started:
            return self

        LoggerManager.logger.info("Iniciando VPZone TTS")

        if self.headless:
            self.banner()

        # Limpieza de audios temporales de sesiones anteriores
        self._clean_temp(startup=True)

        # Cliente REST de VPZone
        self.api = VPZoneClient(
            base_url=self.config.get("api_base_url"),
            api_key=self.config.get("api_key")
        )

        # Iniciar todos los servicios (TTS + plugins)
        self.services.start()

        # Iniciar conexiones
        self.connection = ConnectionManager(
            self.events,
            self.config
        )

        self.connection.start()

        self.started = True

        self.events.emit("program.started", self.info())

        # Auto-borrado periódico de la carpeta temporal
        self._start_temp_janitor()

        return self

    def stop(self):

        if not self.started:
            return

        LoggerManager.logger.info("Deteniendo VPZone TTS")

        self.services.stop()

        if self.connection:
            self.connection.stop()

        self.started = False

        # Última limpieza de temporales al cerrar
        self._clean_temp()

        self.events.emit("program.stopped", {})

    # ------------------------------------------------------------------ #

    def _clean_temp(self, startup=False):
        """Borra el contenido de la carpeta temporal (si está habilitado)."""

        if not self.config.get("tts.auto_clean_temp", True):
            return

        removed = purge_temp()

        if removed and startup:
            LoggerManager.logger.info(
                f"Temp: {removed} archivo(s) antiguo(s) eliminado(s)"
            )

    def _start_temp_janitor(self):
        """Lanza un hilo que limpia la carpeta temporal periódicamente."""

        if not self.config.get("tts.auto_clean_temp", True):
            return

        interval = self.config.get("tts.temp_clean_interval", 120)

        try:
            interval = max(15, int(interval))
        except (TypeError, ValueError):
            interval = 120

        def _loop():

            while not self._shutdown.wait(interval):

                removed = purge_temp()

                if removed:
                    LoggerManager.logger.debug(
                        f"Temp: {removed} archivo(s) eliminado(s)"
                    )

        self._temp_thread = threading.Thread(
            target=_loop,
            name="temp-janitor",
            daemon=True
        )

        self._temp_thread.start()

    def run(self):

        """Mantiene el proceso vivo hasta pedir la salida (modo consola)."""

        self.start()

        try:

            while not self._shutdown.wait(0.5):
                pass

        except KeyboardInterrupt:

            print("\nSaliendo...")

        finally:

            self.stop()

    def shutdown(self):

        self._shutdown.set()

    def banner(self):

        print("=" * 45)
        print(f" {APP_NAME}")
        print("=" * 45)
        print("Versión :", self.config.get("version", VERSION))
        print("Canal   :", self.config.get("channel"))
        print("Voz     :", self.config.get("tts.voice"))
        print("=" * 45)

    def info(self):

        return {
            "app": APP_NAME,
            "version": self.config.get("version", VERSION),
            "channel": self.config.get("channel"),
            "provider": self.config.get("tts.provider"),
            "voice": self.config.get("tts.voice"),
            "started": self.started
        }
