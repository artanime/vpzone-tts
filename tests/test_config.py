from core.config_manager import ConfigManager

config = ConfigManager()
config.load()

print(config.get("version"))
print(config.get("channel"))
print(config.get("tts.filters.url"))
print(config.get("tts.filters.emoji"))