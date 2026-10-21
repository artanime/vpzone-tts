"""Valores por defecto de la configuración.

Cualquier clave ausente en config/config.json se rellena con estos valores.
"""

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "language": "es",
    "platform": "vpzone",
    "channel": "",
    "api_base_url": "https://vpzone.tv/api/v1",
    "api_key": "",
    "websocket_url": "wss://chat.vpzone.tv/ws",
    "woupi": {
        "client_id": "",
        "access_token": "",
        "refresh_token": "",
        "scopes": "chat:read",
        "broadcaster_id": "",
        "user_id": "",
        "ignore_own_messages": False,
        "api_base_url": "https://api.woupi.buzz",
        "eventsub_url": "wss://api.woupi.buzz/eventsub"
    },
    "tts": {
        "provider": "piper",
        "voice": "default",
        "volume": 100,
        "speed": 1.0,
        "max_queue": 100,
        "read_username": True,
        "skip_history": True,
        "auto_clean_temp": True,
        "temp_clean_interval": 120,
        "filters": {
            "length": True,
            "url": True,
            "emoji": True,
            "duplicate": True,
            "spam": True,
            "replace": False
        }
    }
}
