import threading

from core.logger_manager import LoggerManager


class TTSEngine:
    """Hilo dedicado que consume la cola y envía el texto al proveedor."""

    def __init__(self, provider, queue_manager, on_start=None, on_done=None):

        self.provider = provider
        self.queue = queue_manager

        # Callbacks opcionales: se ejecutan en el hilo del motor.
        self.on_start = on_start
        self.on_done = on_done

        self.running = False

        self.thread = None

    @property
    def is_running(self):

        return self.running and self.thread is not None and self.thread.is_alive()

    def start_engine(self):

        if self.is_running:
            return

        LoggerManager.logger.info("Iniciando TTSEngine")

        self.provider.load()

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            name="TTSEngine",
            daemon=True
        )

        self.thread.start()

    def run(self):

        while self.running:

            message = self.queue.next(timeout=0.5)

            if message is None:
                continue

            try:

                if self.on_start:

                    self.on_start(message)

                self.provider.speak(message.text)

                if self.on_done:

                    self.on_done(message)

            except Exception as e:

                LoggerManager.logger.exception(f"Error reproduciendo mensaje: {e}")

        LoggerManager.logger.info("TTSEngine detenido")

    def stop_engine(self):

        if not self.running and self.thread is None:
            return

        self.running = False

        thread = self.thread

        if thread is not None and thread.is_alive():

            thread.join(timeout=3)

        self.thread = None

        try:

            self.provider.stop()
            self.provider.close()

        except Exception as e:

            LoggerManager.logger.exception(f"Error cerrando el proveedor: {e}")
