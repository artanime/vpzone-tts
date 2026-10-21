import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tts.queue_manager import QueueManager
from tts.models import TTSMessage

cola = QueueManager()

cola.add(
    TTSMessage(
        text="Usuario normal",
        priority=0
    )
)

cola.add(
    TTSMessage(
        text="Moderador",
        priority=10
    )
)

cola.add(
    TTSMessage(
        text="Streamer",
        priority=100
    )
)

while not cola.empty():

    msg = cola.next()

    print(msg.priority, msg.text)