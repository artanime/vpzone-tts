"""Constantes globales de la aplicación."""

APP_NAME = "VPZone TTS"

VERSION = "1.0.0"

AUTHOR = "ArtAnime2"

# Client ID de la aplicación pública de Woupi (NO es un secreto: los clientes
# públicos solo usan el flujo de código de dispositivo, sin client_secret).
# Rellénalo con el client_id de tu app pública creada en https://dev.woupi.buzz
WOUPI_CLIENT_ID = "caoc5ah6lg4ed92qok8tydb686odg1"

# Permisos solicitados al autorizar Woupi (separados por espacios).
WOUPI_SCOPES = "chat:read"

CONFIG_FOLDER = "config"

LOG_FOLDER = "logs"

VOICE_FOLDER = "voices"

AUDIO_FOLDER = "audio"

TEMP_FOLDER = "temp"

PLUGIN_FOLDER = "plugins"
