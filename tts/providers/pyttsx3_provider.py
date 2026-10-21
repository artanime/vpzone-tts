"""Proveedor TTS local usando SAPI5 vía `pyttsx3` (funciona sin internet)."""

from core.logger_manager import LoggerManager
from tts.capabilities import Capability
from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory

DEFAULT_RATE = 200


def _engine_voice(engine, wanted):
    """Busca la voz por id o por nombre; si no, devuelve la predeterminada."""

    if not wanted or wanted == "default":
        return None

    voices = engine.getProperty("voices") or []

    wanted = wanted.lower()

    for voice in voices:

        if wanted in str(voice.id).lower() or wanted in str(voice.name).lower():
            return voice.id

    return None


class Pyttsx3Provider(BaseProvider):

    name = "pyttsx3"

    def load(self):
        LoggerManager.logger.info(
            f"pyttsx3 cargado (voz={self.voice}, "
            f"velocidad={self.speed}, volumen={self.volume})"
        )

    def speak(self, text):

        if not text or not text.strip():
            return

        engine = None

        try:

            import pyttsx3

            engine = pyttsx3.init()

            engine.setProperty(
                "rate",
                max(50, int(DEFAULT_RATE * self.speed))
            )

            engine.setProperty(
                "volume",
                max(0.0, min(1.0, self.volume / 100.0))
            )

            voice_id = _engine_voice(engine, self.voice)

            if voice_id:
                engine.setProperty("voice", voice_id)

            engine.say(text)

            engine.runAndWait()

        except Exception as exc:

            LoggerManager.logger.error(f"pyttsx3 no pudo reproducir: {exc}")

        finally:

            if engine is not None:

                try:
                    engine.stop()
                except Exception:
                    pass

    @staticmethod
    def list_voices():

        try:

            import pyttsx3

            engine = pyttsx3.init()

            voices = engine.getProperty("voices") or []

            result = []
            seen = set()

            for voice in voices:

                voice_id = str(voice.id)

                if voice_id in seen:
                    continue

                seen.add(voice_id)

                result.append({
                    "name": str(getattr(voice, "name", "") or ""),
                    "id": voice_id,
                    "locale": ", ".join(
                        str(lang) for lang in (getattr(voice, "languages", []) or [])
                    ),
                    "gender": str(getattr(voice, "gender", "") or "")
                })

            try:
                engine.stop()
            except Exception:
                pass

            return result

        except Exception as exc:

            LoggerManager.logger.warning(f"No se pudieron listar voces: {exc}")

            return []


ProviderFactory.register(

    name="pyttsx3",

    provider=Pyttsx3Provider,

    version="1.0.0",

    author="VPZone",

    description="SAPI5 local de Windows (sin internet)",

    local=True,

    cloud=False,

    gpu=False,

    languages=["*"],

    priority=5,

    capabilities=[
        Capability.LOCAL,
        Capability.OFFLINE,
        Capability.FAST
    ]
)
