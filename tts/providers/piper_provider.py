"""Proveedor TTS neuronal local usando Piper (offline).

Genera audio WAV con los modelos ONNX de Piper y lo reproduce con
`AudioPlayer`. No requiere internet ni Microsoft Edge; funciona siempre.

Los modelos de voz se guardan en `voices/piper/<nombre>.onnx` junto a su
fichero de configuración `<nombre>.onnx.json`.
"""

import threading
import time
import wave

from core.logger_manager import LoggerManager
from core.paths import VOICE_DIR, TEMP_DIR, ensure_folders
from tts.audio.player import AudioPlayer
from tts.capabilities import Capability
from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory

MODEL_DIR = VOICE_DIR / "piper"

DEFAULT_MODEL = "es_ES-davefx-medium"


def _models():
    """Devuelve {nombre_sin_extension: ruta_onnx} de los modelos instalados."""

    if not MODEL_DIR.is_dir():
        return {}

    result = {}

    for path in sorted(MODEL_DIR.glob("*.onnx")):

        if path.name.endswith(".onnx.json"):
            continue

        result[path.stem] = path

    return result


def _locale_from_name(name):
    """Extrae el locale (ej. 'es_ES') a partir del nombre del modelo."""

    parts = name.split("-")

    if len(parts) >= 2 and "_" in parts[0]:
        return parts[0]

    return ""


class PiperProvider(BaseProvider):

    name = "piper"

    # Cache de voces cargadas: cargar un modelo ONNX es costoso.
    _cache = {}
    _lock = threading.Lock()

    def __init__(self, config=None):

        super().__init__(config)

        self.player = AudioPlayer()

    def _current_model(self):

        models = _models()

        if not models:
            return None, None

        wanted = self.voice

        if wanted and wanted not in (None, "", "default"):

            key = str(wanted)

            if key.endswith(".onnx"):
                key = key[:-5]

            if key in models:
                return key, models[key]

            for name, path in models.items():
                if key.lower() in name.lower():
                    return name, path

        if DEFAULT_MODEL in models:
            return DEFAULT_MODEL, models[DEFAULT_MODEL]

        name = next(iter(models))

        return name, models[name]

    def _voice(self, model_path):

        key = str(model_path)

        with PiperProvider._lock:

            cached = PiperProvider._cache.get(key)

            if cached is not None:
                return cached

            from piper import PiperVoice

            voice = PiperVoice.load(key)

            PiperProvider._cache[key] = voice

            return voice

    def load(self):

        ensure_folders()

        name, path = self._current_model()

        if path is None:

            LoggerManager.logger.warning(
                f"Piper: no hay modelos en {MODEL_DIR}. "
                f"Descarga uno (ej. {DEFAULT_MODEL}.onnx y .onnx.json)."
            )

            return

        LoggerManager.logger.info(
            f"Piper cargado (voz={name}, velocidad={self.speed}, "
            f"volumen={self.volume})"
        )

    def speak(self, text):

        if not text or not text.strip():
            return

        name, path = self._current_model()

        if path is None:

            LoggerManager.logger.error(
                "Piper: no hay ningún modelo de voz instalado"
            )

            return

        wav_path = TEMP_DIR / f"piper_{int(time.time() * 1000)}.wav"

        try:

            self._synthesize(text, path, wav_path)

            self.player.play(str(wav_path), volume=self.volume, wait=True)

        except Exception as exc:

            LoggerManager.logger.error(f"Piper no pudo reproducir: {exc}")

        finally:

            AudioPlayer.cleanup(str(wav_path))

    def _synthesize(self, text, model_path, wav_path):

        from piper import SynthesisConfig

        voice = self._voice(model_path)

        # En Piper, length_scale mayor = más lento. speed > 1 = más rápido.
        speed = self.speed if self.speed else 1.0

        length_scale = max(0.4, min(2.5, 1.0 / speed))

        syn_config = SynthesisConfig(
            length_scale=length_scale,
            normalize_audio=True
        )

        with wave.open(str(wav_path), "wb") as wav_file:

            voice.synthesize_wav(
                text,
                wav_file,
                syn_config=syn_config
            )

    def stop(self):

        self.player.stop()

    @staticmethod
    def list_voices():

        return [
            {
                "name": name,
                "id": name,
                "locale": _locale_from_name(name),
                "gender": ""
            }
            for name in _models()
        ]


ProviderFactory.register(

    name="piper",

    provider=PiperProvider,

    version="1.0.0",

    author="VPZone",

    description="Piper TTS neuronal local (offline, sin internet)",

    local=True,

    cloud=False,

    gpu=False,

    languages=["es", "en", "pt", "fr", "de", "it"],

    priority=8,

    capabilities=[
        Capability.LOCAL,
        Capability.OFFLINE,
        Capability.FAST,
        Capability.MULTILINGUAL
    ]
)
