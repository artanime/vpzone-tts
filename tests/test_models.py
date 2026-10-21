import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.models.chat_message import ChatMessage


data = {

    "id": 1,

    "message": "Hola VPZone!",

    "created_at": "2026-07-31",

    "author": {

        "id": 10,

        "username": "usuario",

        "display_name": "Usuario",

        "verified": True

    }

}

message = ChatMessage.from_json(data)

print(message)

print()

print(message.author.display_name)

print(message.message)
