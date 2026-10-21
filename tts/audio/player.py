"""Reproducción de audio.

Backend principal: `pygame-ce` (SDL) para reproducir MP3/WAV.
Backend de respaldo: `ffplay` (ffmpeg) por subproceso.
Si ninguno está disponible, la reproducción se salta silenciosamente y se
registra un aviso en el log.
"""

import os
import shutil
import subprocess
import threading
import time

from core.logger_manager import LoggerManager


class AudioPlayer:

    def __init__(self):

        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()

        self._backend = None
        self._initialized = False

    @property
    def backend(self):

        self._init()

        return self._backend

    @property
    def available(self):

        return self.backend is not None

    def _init(self):

        if self._initialized:
            return

        with self._state_lock:

            if self._initialized:
                return

            self._backend = self._detect()
            self._initialized = True

    @staticmethod
    def _detect():

        try:

            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)

            LoggerManager.logger.info("Audio: backend pygame (SDL) listo")

            return "pygame"

        except Exception as exc:

            LoggerManager.logger.warning(f"Audio: pygame no disponible ({exc})")

        if shutil.which("ffplay"):

            LoggerManager.logger.info("Audio: backend ffplay listo")

            return "ffplay"

        LoggerManager.logger.warning(
            "Audio: sin backend, no se reproducirá nada"
        )

        return None

    def play(self, path, volume=100, wait=True):

        self._init()

        if self._backend is None or not path or not os.path.exists(path):

            if path and os.path.exists(path):
                self.cleanup(path)

            return False

        self._stop_event.clear()

        try:

            if self._backend == "pygame":
                return self._play_pygame(path, volume, wait)

            return self._play_ffplay(path, volume, wait)

        except Exception as exc:

            LoggerManager.logger.exception(f"Audio: error reproduciendo {path}: {exc}")

            return False

    def _play_pygame(self, path, volume, wait):

        import pygame

        pygame.mixer.music.load(path)

        pygame.mixer.music.set_volume(self._clamp(volume))

        pygame.mixer.music.play()

        if not wait:
            return True

        try:

            while pygame.mixer.music.get_busy():

                if self._stop_event.is_set():

                    pygame.mixer.music.stop()

                    break

                time.sleep(0.05)

        finally:

            # Libera el archivo para poder borrarlo (Windows bloquea si sigue
            # cargado).
            self._unload_music(pygame)

        return True

    @staticmethod
    def _unload_music(pygame):

        try:

            unload = getattr(pygame.mixer.music, "unload", None)

            if unload:
                unload()

        except Exception:

            pass

    def _play_ffplay(self, path, volume, wait):

        process = subprocess.Popen(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel", "quiet",
                "-volume", str(int(self._clamp(volume) * 100)),
                path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if not wait:
            return True

        while process.poll() is None:

            if self._stop_event.is_set():

                process.terminate()

                break

            time.sleep(0.05)

        return True

    def stop(self):

        self._stop_event.set()

        if self._backend == "pygame":

            try:

                import pygame

                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    self._unload_music(pygame)

            except Exception:

                pass

    @staticmethod
    def _clamp(volume):

        try:
            value = float(volume)
        except (TypeError, ValueError):
            value = 100.0

        return max(0.0, min(1.0, value / 100.0))

    @staticmethod
    def cleanup(path, retries=5):

        if not path:
            return

        for _ in range(max(1, retries)):

            try:

                if os.path.exists(path):
                    os.remove(path)

                return

            except OSError:

                time.sleep(0.1)
