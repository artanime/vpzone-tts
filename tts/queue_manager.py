from queue import Empty, PriorityQueue

from core.logger_manager import LoggerManager
from tts.models import TTSMessage


class QueueManager:
    """Cola con prioridad (la más alta se lee primero).

    Usa una clave `(-prioridad, contador)` para no tener que comparar
    mensajes entre sí, evitando el `TypeError` al tener dos mensajes con la
    misma prioridad.
    """

    def __init__(self, max_size=100):

        self.queue = PriorityQueue()

        if not isinstance(max_size, int) or max_size <= 0:
            max_size = 100

        self.max_size = max_size

        self._sequence = 0

    def add(self, message):

        if message is None:
            return False

        # Si nos pasan un texto normal, lo convertimos automáticamente
        if isinstance(message, str):
            message = TTSMessage(text=message)

        # Evitar que la cola crezca demasiado
        if self.queue.qsize() >= self.max_size:

            LoggerManager.logger.warning("[TTS] Cola llena, mensaje descartado")

            return False

        self._sequence += 1

        # PriorityQueue devuelve primero el elemento con la clave menor.
        self.queue.put((-int(message.priority), self._sequence, message))

        return True

    def next(self, timeout=0.5):
        """Extrae el siguiente mensaje; devuelve None si se vacía el tiempo."""

        try:

            _, _, message = self.queue.get(timeout=timeout)

        except Empty:

            return None

        except Exception as exc:

            LoggerManager.logger.exception(exc)

            return None

        return message

    def size(self):

        return self.queue.qsize()

    def empty(self):

        return self.queue.empty()

    def clear(self):

        drained = 0

        while not self.queue.empty():

            try:
                self.queue.get_nowait()
                drained += 1
            except Empty:
                break

        return drained
