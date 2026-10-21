import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.config_manager import ConfigManager
from core.event_manager import EventManager
from tts.service import TTSService


config = ConfigManager()
config.load()

# Usamos el proveedor "fake" (solo imprime) para el test.
config.set("tts.provider", "fake")

events = EventManager()

service = TTSService(config, events)

service.start()

service.speak("Hola usuario")
service.speak("Bienvenido a VPZone")
service.speak("Este es el motor TTS")

# Esperar a que la cola se vacíe
while service.pending:

    time.sleep(0.1)

time.sleep(0.4)

service.stop()

print("test_tts OK")
