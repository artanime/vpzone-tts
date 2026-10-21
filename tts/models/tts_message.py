from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TTSMessage:

    text: str

    username: str = ""

    display_name: str = ""

    role: str = "viewer"

    language: str = "auto"

    priority: int = 0

    voice: str | None = None

    channel: str = ""

    timestamp: datetime = field(default_factory=datetime.now)

    metadata: dict = field(default_factory=dict)

    def to_dict(self):

        return {
            "text": self.text,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "language": self.language,
            "priority": self.priority,
            "voice": self.voice,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
