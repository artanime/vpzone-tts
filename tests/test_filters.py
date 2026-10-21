from tts.models import TTSMessage

from tts.filter_manager import FilterManager

from core.config_manager import ConfigManager

from tts.models import TTSMessage
from tts.filter_registry import FilterRegistry


# Cargar configuración
config = ConfigManager()
config.load()

# Crear filtros desde la configuración
filters = FilterRegistry(config).build()


tests = [
    "AAAAAAAAAAAAAAAAAAAAAA",
    "!!!!!!!!!!!!!!!!!",
    "Hola 😀 visita https://vpzone.tv",
    "Hola VPZone",
    "Hola VPZone"
]


for text in tests:

    message = TTSMessage(
        text=text,
        username="usuario"
    )

    result = filters.process(message)

    if result is None:

        print(f"[BLOQUEADO] {text}")

    else:

        print(f"[OK] {result.text}")
