from core.logger_manager import LoggerManager
from tts.engine import TTSEngine
from tts.queue_manager import QueueManager
from tts.voice_manager import VoiceManager
from tts.models import TTSMessage

from tts.filter_registry import FilterRegistry
from tts.provider_factory import ProviderFactory


class TTSService:

    def __init__(self, config, events):

        # Referencias
        self.config = config
        self.events = events

        # Cola de mensajes
        self.queue = QueueManager(
            max_size=self.config.get("tts.max_queue", 100)
        )

        # Gestor de filtros (se construye desde la configuración)
        self.filters = FilterRegistry(self.config).build()

        # Proveedor de voz
        self.voice_manager = VoiceManager(config)
        self.provider = self.voice_manager.provider()

        # Motor TTS
        self.engine = TTSEngine(
            self.provider,
            self.queue,
            on_start=self._on_speaking,
            on_done=self._on_spoken
        )

        # Registrar eventos
        self.register_events()

    def register_events(self):

        self.events.on("tts.speak", self.on_tts_speak)

    def start(self):

        LoggerManager.logger.info("TTS: servicio iniciado")

        self.engine.start_engine()

        self.events.emit("tts.started")

    def stop(self):

        LoggerManager.logger.info("TTS: servicio detenido")

        self.engine.stop_engine()

        self.events.emit("tts.stopped")

    def speak(self, text, username="", display_name="", priority=0):

        if not text:
            return

        self.events.emit(
            "tts.speak",
            {
                "text": text,
                "username": username,
                "display_name": display_name,
                "priority": priority
            }
        )

    def refresh(self):
        """Reaplica los filtros y, si cambió, instala otro proveedor."""

        self.filters = FilterRegistry(self.config).build()

        target = self.config.get("tts.provider")

        if target and getattr(self.provider, "name", None) != target:

            if ProviderFactory.exists(target):

                try:

                    provider = ProviderFactory.create(target, self.config)

                    provider.load()

                    self.provider = provider

                    self.engine.provider = provider

                    LoggerManager.logger.info(
                        f"TTS: proveedor cambiado a '{target}'"
                    )

                except Exception as exc:

                    LoggerManager.logger.error(
                        f"No se pudo cambiar el proveedor a '{target}': {exc}"
                    )

        return self.provider

    def on_tts_speak(self, data):

        if not data:
            return

        text = (data.get("text") or "").strip()

        if not text:
            return

        message = TTSMessage(
            text=text,
            username=data.get("username", ""),
            display_name=data.get("display_name", ""),
            role=data.get("role", "viewer"),
            language=data.get("language", "auto"),
            priority=data.get("priority", 0),
            voice=data.get("voice"),
            channel=data.get("channel", "")
        )

        # Aplicar filtros
        filtered = self.filters.process(message)

        if filtered is None:

            self.events.emit(
                "tts.rejected",
                {
                    "message": message.to_dict(),
                    "reason": self.filters.last_blocked_by or "filtro"
                }
            )

            return

        # Añadir a la cola
        self.queue.add(filtered)

        self.events.emit(
            "tts.queued",
            {
                "message": filtered.to_dict(),
                "size": self.queue.size()
            }
        )

    def _on_speaking(self, message):

        self.events.emit("tts.speaking", {"message": message.to_dict()})

    def _on_spoken(self, message):

        self.events.emit(
            "tts.spoken",
            {
                "message": message.to_dict(),
                "size": self.queue.size()
            }
        )

    @property
    def speaking(self):

        return self.engine.is_running

    @property
    def pending(self):

        return self.queue.size()

    def clear_queue(self):

        cleared = self.queue.clear()

        self.events.emit("tts.queue.cleared", {"cleared": cleared})

        return cleared
