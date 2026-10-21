from collections import defaultdict

from core.logger_manager import LoggerManager


class EventManager:

    def __init__(self):

        self.listeners = defaultdict(list)

    def on(self, event_name, callback):
        """
        Registrar un listener para un evento.
        """
        self.listeners[event_name].append(callback)

    def once(self, event_name, callback):
        """
        Registrar un listener que solo se ejecutará una vez.
        """

        def wrapper(data):

            callback(data)

            if wrapper in self.listeners[event_name]:
                self.listeners[event_name].remove(wrapper)

        self.listeners[event_name].append(wrapper)

    def emit(self, event_name, data=None):
        """
        Ejecutar todos los listeners registrados.
        """

        if event_name not in self.listeners:
            return

        # Copiamos la lista para evitar errores si un listener
        # elimina otro durante la ejecución.
        for callback in list(self.listeners[event_name]):

            try:
                callback(data)

            except Exception as e:
                LoggerManager.logger.exception(
                    f"Error ejecutando el evento '{event_name}': {e}"
                )

    def remove(self, event_name, callback):
        """
        Eliminar un listener.
        """

        if callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)

    def clear(self, event_name=None):
        """
        Elimina todos los listeners.
        """

        if event_name is None:
            self.listeners.clear()
        else:
            self.listeners[event_name].clear()
