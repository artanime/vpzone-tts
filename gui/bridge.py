"""Puente entre los eventos (que llegan desde otros hilos) y la interfaz.

Los proveedores, el motor TTS y el WebSocket corren en hilos secundarios.
`EventBridge` encola sus eventos y la ventana los drena con `after()`, que
siempre se ejecuta en el hilo principal de Tkinter.
"""

import queue
import traceback

# Eventos que interesan a la interfaz.
BRIDGE_EVENTS = [
    "program.started",
    "program.stopped",
    "connection.open",
    "connection.closed",
    "connection.error",
    "connection.missing_channel",
    "chat.message",
    "tts.started",
    "tts.stopped",
    "tts.queued",
    "tts.rejected",
    "tts.speaking",
    "tts.spoken",
    "tts.queue.cleared"
]


class EventBridge:

    def __init__(self, event_manager, events=None):

        self.events = event_manager

        self.queue = queue.Queue()

        self._subscriptions = []

        for name in (events or BRIDGE_EVENTS):
            self.subscribe(name)

    def subscribe(self, name):

        callback = self._listener(name)

        self.events.on(name, callback)

        self._subscriptions.append((name, callback))

    def _listener(self, name):

        def handler(data):

            self.queue.put((name, data))

        return handler

    def drain(self, handle):
        """Procesa todos los eventos pendientes. Devuelve cuántos."""

        processed = 0

        while True:

            try:

                name, data = self.queue.get_nowait()

            except queue.Empty:

                break

            try:

                handle(name, data)

                processed += 1

            except Exception:

                traceback.print_exc()

        return processed

    def pending(self):

        return self.queue.qsize()

    def close(self):

        for name, callback in self._subscriptions:

            self.events.remove(name, callback)

        self._subscriptions.clear()

        while True:

            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
