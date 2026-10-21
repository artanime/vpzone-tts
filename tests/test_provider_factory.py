from core.config_manager import ConfigManager
from tts.voice_manager import VoiceManager

config = ConfigManager()
config.load()

voice = VoiceManager(config)

provider = voice.provider()

print(type(provider).__name__)
print("Proveedores registrados:", provider.__class__.__name__)