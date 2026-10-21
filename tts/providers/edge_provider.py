"""Proveedor TTS basado en Microsoft Edge (online).

Genera audio MP3 mediante `edge-tts` y lo reproduce con `AudioPlayer`.
Requiere conexión a internet.
"""

import asyncio
import time

from core.logger_manager import LoggerManager
from core.paths import TEMP_DIR, ensure_folders
from tts.audio.player import AudioPlayer
from tts.capabilities import Capability
from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory

# Voces recomendadas por defecto (muestra de es/pt/en).
POPULAR_VOICES = [
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "es-MX-JorgeNeural",
    "es-MX-DaliaNeural",
    "es-AR-TomasNeural",
    "es-AR-ElenaNeural",
    "es-US-AlonsoNeural",
    "es-US-PalomaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "pt-BR-AntonioNeural",
    "pt-BR-FranciscaNeural"
]

SYNTH_TIMEOUT = 60


def _percent(value):

    value = max(-100, min(100, int(value)))

    return f"+{value}%" if value >= 0 else f"{value}%"


class EdgeProvider(BaseProvider):

    name = "edge"

    def __init__(self, config=None):

        super().__init__(config)

        self.player = AudioPlayer()

    def load(self):

        ensure_folders()

        LoggerManager.logger.info(
            f"Edge TTS cargado (voz={self._current_voice()}, "
            f"velocidad={self.speed}, volumen={self.volume})"
        )

    def _current_voice(self):

        voice = self.voice

        if voice in (None, "", "default"):
            return POPULAR_VOICES[0]

        return voice

    def speak(self, text):

        if not text or not text.strip():
            return

        path = self._synthesize(text)

        if path is None:
            return

        try:

            self.player.play(path, volume=self.volume, wait=True)

        finally:

            AudioPlayer.cleanup(path)

    def _synthesize(self, text):

        path = TEMP_DIR / f"edge_{int(time.time() * 1000)}.mp3"

        last_error = None

        for attempt in range(1, 4):

            try:

                asyncio.run(self._write_audio(text, str(path)))

                return str(path)

            except Exception as exc:

                last_error = exc

                LoggerManager.logger.warning(
                    f"Edge TTS intento {attempt}/3 falló: {exc}"
                )

                time.sleep(1.5 * attempt)

        LoggerManager.logger.error(
            f"Edge TTS no pudo generar audio: {last_error}"
        )

        AudioPlayer.cleanup(path)

        return None

    async def _write_audio(self, text, path):

        import edge_tts

        communicate = edge_tts.Communicate(
            text=text,
            voice=self._current_voice(),
            rate=_percent((self.speed - 1.0) * 100),
            volume=_percent(self.volume - 100)
        )

        await asyncio.wait_for(
            communicate.save(path),
            timeout=SYNTH_TIMEOUT
        )

    def stop(self):

        self.player.stop()

    @staticmethod
    def list_voices(timeout=15):
        """Devuelve la lista de voces disponibles (requiere internet)."""

        async def _fetch():

            import edge_tts

            voices = await asyncio.wait_for(
                edge_tts.list_voices(),
                timeout=timeout
            )

            return [
                {
                    "name": voice.get("ShortName", ""),
                    "locale": voice.get("Locale", ""),
                    "gender": voice.get("Gender", "")
                }
                for voice in voices
            ]

        try:

            return asyncio.run(_fetch())

        except Exception as exc:

            LoggerManager.logger.warning(
                f"No se pudo obtener la lista de voces de Edge: {exc}"
            )

            return [
                {"name": name, "locale": name.rsplit("-", 1)[0], "gender": ""}
                for name in POPULAR_VOICES
            ]


ProviderFactory.register(

    name="edge",

    provider=EdgeProvider,

    version="1.0.0",

    author="VPZone",

    description="Microsoft Edge TTS (voz de alta calidad, online)",

    local=False,

    cloud=True,

    gpu=False,

    languages=["es", "en", "pt", "fr", "de", "it", "ja"],

    priority=10,

    capabilities=[
        Capability.CLOUD,
        Capability.MULTILINGUAL,
        Capability.FAST
    ]
)
