from abc import ABC, abstractmethod


class BaseProvider(ABC):

    # Nombre con el que se registra el proveedor.
    name = "unknown"

    def __init__(self, config=None):

        self.config = config

    def get(self, key, default=None):
        """Lee una clave soportando rutas puntualadas (ej: "tts.voice")."""

        if self.config is None:
            return default

        return self.config.get(key, default)

    @property
    def voice(self):
        return self.get("tts.voice", "default")

    @property
    def volume(self):
        return self.get("tts.volume", 100)

    @property
    def speed(self):
        return float(self.get("tts.speed", 1.0))

    def load(self):
        """
        Inicializar el proveedor.
        """
        pass

    @abstractmethod
    def speak(self, text):
        """
        Reproducir un texto (bloquea hasta terminar).
        """
        pass

    def stop(self):
        """
        Detener reproducción.
        """
        pass

    def close(self):
        """
        Liberar recursos.
        """
        pass
