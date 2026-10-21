"""Ventana principal de VPZone TTS (CustomTkinter)."""

import threading
import queue

import customtkinter as ctk

from core.constants import APP_NAME, VERSION, WOUPI_CLIENT_ID
from core.logger_manager import LoggerManager

from gui.bridge import EventBridge
from gui.i18n import LANGUAGE_BY_NAME, i18n
from gui.panels import (
    APP_ACCENT,
    ERROR_COLOR,
    PLATFORM_BY_NAME,
    FiltersPanel,
    HeaderBar,
    LogPanel,
    SettingsPanel,
    VoiceTestPanel
)
from gui.woupi_auth import WoupiAuthDialog

from tts.providers.edge_provider import EdgeProvider
from tts.providers.piper_provider import PiperProvider
from tts.providers.pyttsx3_provider import Pyttsx3Provider


def _list_voices(provider_name):
    """Devuelve (etiquetas, valores) para el desplegable de voces."""

    default_label = i18n.t("voice.default")

    if provider_name == "piper":

        labels = [default_label]
        values = ["default"]

        for voice in PiperProvider.list_voices():

            name = voice.get("name") or "voz"

            locale = voice.get("locale")

            label = f"{name} ({locale})" if locale else name

            while label in labels:
                label = f"{label} "

            labels.append(label)

            values.append(voice.get("id") or name)

        return (labels, values)

    if provider_name == "edge":

        labels = [default_label]
        values = ["default"]

        for voice in EdgeProvider.list_voices():

            labels.append(voice["name"])

            values.append(voice["name"])

        return (labels, values)

    if provider_name == "pyttsx3":

        labels = [default_label]
        values = ["default"]

        for voice in Pyttsx3Provider.list_voices():

            label = voice.get("name") or voice.get("id") or "voz"

            locale = voice.get("locale")

            if locale:
                label = f"{label} ({locale})"

            while label in labels:
                label = f"{label} "

            labels.append(label)

            values.append(voice.get("id") or label)

        return (labels, values)

    return ([default_label], ["default"])


class VPZoneGUI(ctk.CTk):

    def __init__(self, app):

        super().__init__()

        self.app = app
        self.config = app.config

        i18n.set_language(self.config.get("language", "es"))

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1050x680")
        self.minsize(900, 600)

        self._set_window_icon()
        self._closing = False
        self._dirty = False
        self._save_job = None
        self._loading_voices = False
        self._voice_labels = []
        self._voice_values = []
        self._voice_results = queue.Queue()
        self._woupi_dialog = None

        # ---------- Layout ----------
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.header = HeaderBar(self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.panel_settings = SettingsPanel(self, self.callbacks())
        self.panel_settings.grid(
            row=1, column=0, sticky="nsw", padx=12, pady=12
        )

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(0, 12), pady=12)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.panel_filters = FiltersPanel(right, self.on_filter_toggle)
        self.panel_filters.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.panel_test = VoiceTestPanel(
            right,
            on_speak=self.on_test_speak,
            on_clear=self.on_clear_queue
        )
        self.panel_test.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        plug_row = ctk.CTkFrame(right, fg_color="transparent")
        plug_row.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.plugins_label = ctk.CTkLabel(
            plug_row, text="Plugins: -", anchor="w"
        )
        self.plugins_label.grid(row=0, column=0, sticky="ew", padx=2)

        self.panel_log = LogPanel(right)
        self.panel_log.grid(row=3, column=0, sticky="nsew")

        # ---------- Eventos ----------
        self.bridge = EventBridge(app.events)

        # ---------- Arranque ----------
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.load_config_into_ui()

        app.services.start()

        self.refresh_plugin_status()

        self._load_voices(selected=self.config.get("tts.voice"))

        self.panel_log.add("INFO", "log.ready")
        self.panel_log.add(
            "AVISO",
            "log.ws_hint"
        )

        self.after(80, self._poll)

    # ------------------------------------------------------------------ #

    def _set_window_icon(self):
        """Establece el icono de la ventana con el logo del proyecto."""

        from PIL import Image, ImageTk

        from gui.panels import LOGO_PATH

        try:

            if not LOGO_PATH.exists():
                return

            image = Image.open(LOGO_PATH)

            # tkinter exige un PhotoImage del mismo hilo; conservamos referencia.
            self._icon_image = ImageTk.PhotoImage(image)

            self.iconphoto(True, self._icon_image)

        except Exception as exc:

            LoggerManager.logger.warning(f"No se pudo cargar el icono: {exc}")

    def callbacks(self):

        return {
            "apply_channel": self.on_apply_channel,
            "language_changed": self.on_language_changed,
            "platform_changed": self.on_platform_changed,
            "provider_changed": self.on_provider_changed,
            "voice_changed": self.on_voice_changed,
            "refresh_voices": self.on_refresh_voices,
            "volume_changed": self.on_volume_changed,
            "speed_changed": self.on_speed_changed,
            "read_username_changed": self.on_read_username_changed,
            "start_tts": self.on_start_tts,
            "stop_tts": self.on_stop_tts,
            "connect": self.on_connect,
            "disconnect": self.on_disconnect,
            "woupi_account": self.on_woupi_account
        }

    def load_config_into_ui(self):

        filters = self.config.get("tts.filters", {})

        labels, values = _list_voices(self.config.get("tts.provider"))

        self._voice_labels = labels
        self._voice_values = values

        providers = self.app.tts.voice_manager.names()

        self.panel_settings.set_providers(providers, self.config.get("tts.provider"))

        self.panel_settings.set_values(
            channel=self.config.get("channel"),
            provider=self.config.get("tts.provider"),
            volume=self.config.get("tts.volume", 100),
            speed=float(self.config.get("tts.speed", 1.0)),
            read_username=bool(self.config.get("tts.read_username", True))
        )

        self.panel_settings.set_platform(self.config.get("platform", "vpzone"))

        self.panel_settings.set_voices(
            labels,
            self._voice_label_for(self.config.get("tts.voice"))
        )

        self.panel_filters.set_values(filters)

        self.header.set_provider(self.config.get("tts.provider"))

    def _voice_label_for(self, value):

        try:

            return self._voice_labels[self._voice_values.index(value)]

        except (ValueError, IndexError):

            return self._voice_labels[0] if self._voice_labels else i18n.t("voice.default")

    # ------------------------------------------------------------------ #
    # Configuración

    def on_apply_channel(self, value):

        from api.websocket_client import (
            normalize_channel,
            valid_channel
        )

        channel = normalize_channel(value)

        if not channel:
            self.panel_log.add("AVISO", "log.channel.empty")
            return

        self.panel_settings.set_channel(channel)

        self.config.set("channel", channel)
        self._mark_dirty()

        # Woupi usa logins (no el slug de VPZone): no validamos con su patrón.
        if (self.config.get("platform") or "vpzone").lower() == "woupi":

            if " " in channel:
                self.panel_log.add("AVISO", "log.channel.dubious")
            else:
                self.panel_log.add(
                    "OK", "log.channel.set", channel=channel
                )

            return

        if not valid_channel(channel):
            self.panel_log.add("AVISO", "log.channel.dubious")
        else:
            self.panel_log.add("OK", "log.channel.set", channel=channel)

    def on_platform_changed(self, name):

        code = PLATFORM_BY_NAME.get(name)

        if not code or code == (self.config.get("platform") or "vpzone"):
            return

        # Al cambiar de plataforma hay que reconectar con el cliente nuevo.
        if self.app.connection and self.app.connection.connected:

            self.app.connection.stop()

            self.header.set_connection("disconnected")

        self.config.set("platform", code)
        self._mark_dirty()

        self.panel_log.add(
            "OK", "log.platform.changed", platform=name
        )

    def on_language_changed(self, name):

        code = LANGUAGE_BY_NAME.get(name)

        if not code or code == i18n.language:
            return

        i18n.set_language(code)

        self.config.set("language", code)
        self._mark_dirty()

        self.retranslate()

        self.panel_log.add("OK", "log.language.changed", language=name)

    def retranslate(self):

        self.header.retranslate()
        self.panel_settings.retranslate()
        self.panel_filters.retranslate()
        self.panel_test.retranslate()
        self.panel_log.retranslate()

        if self._voice_labels:

            self._voice_labels[0] = i18n.t("voice.default")

            self.panel_settings.set_voices(
                self._voice_labels,
                self._voice_label_for(self.config.get("tts.voice"))
            )

        self.refresh_plugin_status()

    def on_provider_changed(self, value):

        if value == self.config.get("tts.provider"):
            return

        self.config.set("tts.provider", value)
        self._mark_dirty()

        try:
            self.app.tts.refresh()
        except Exception as exc:
            self.panel_log.write("ERROR", str(exc))

        self.header.set_provider(value)

        self.panel_log.add(
            "OK", "log.provider.selected", provider=value
        )

        self.config.set("tts.voice", "default")

        self._load_voices(selected="default")

    def on_voice_changed(self, value):

        try:

            voice = self._voice_values[self._voice_labels.index(value)]

        except (ValueError, IndexError):

            voice = value or "default"

        self.config.set("tts.voice", voice)
        self._mark_dirty()

        self.panel_log.add(
            "OK", "log.voice.selected", voice=value
        )

    def on_volume_changed(self, value):

        self.config.set("tts.volume", int(value))
        self._mark_dirty()

    def on_speed_changed(self, value):

        self.config.set("tts.speed", value)
        self._mark_dirty()

    def on_read_username_changed(self, enabled):

        self.config.set("tts.read_username", bool(enabled))
        self._mark_dirty()

    def on_filter_toggle(self, key, enabled):

        self.config.set(key, bool(enabled))
        self._mark_dirty()

        self.app.tts.refresh()

        name = key.split(".")[-1]

        self.panel_log.add(
            "OK",
            "log.filter.on" if enabled else "log.filter.off",
            name=name
        )

    def on_refresh_voices(self):

        if self._loading_voices:
            return

        self.panel_log.add("INFO", "log.voices.updating")

        self._load_voices(selected=self.config.get("tts.voice"))

    # ------------------------------------------------------------------ #
    # Acciones

    def on_start_tts(self):

        self.app.tts.start()

        self.header.set_tts("active")

        self.panel_log.add("OK", "log.tts.started")

    def on_stop_tts(self):

        self.app.tts.stop()

        self.header.set_tts("stopped")

        self.panel_log.add("INFO", "log.tts.stopped")

    def on_connect(self):

        if self.app.connection and self.app.connection.connected:
            self.panel_log.add("AVISO", "log.already.connected")
            return

        # En Woupi hace falta autorizar la cuenta antes de conectar.
        if (self.config.get("platform") or "vpzone").lower() == "woupi":

            if not self._woupi_ready():

                self.open_woupi_auth(connect_after=True)
                return

        self._connect_now()

    def _connect_now(self):

        if self.app.connection is None:

            from core.connection_manager import ConnectionManager

            self.app.connection = ConnectionManager(
                self.app.events,
                self.app.config
            )

        ok = self.app.connection.start()

        if ok:
            self.panel_log.add("INFO", "log.connecting")

    def _woupi_ready(self):
        """¿Hay client_id y access_token de Woupi para intentar conectar?"""

        client_id = (
            (self.config.get("woupi.client_id") or "").strip()
            or WOUPI_CLIENT_ID
        )
        access_token = (self.config.get("woupi.access_token") or "").strip()

        return bool(client_id and access_token)

    def on_woupi_account(self):

        self.open_woupi_auth(connect_after=False)

    def open_woupi_auth(self, connect_after=False):
        """Abre el asistente de autorización de Woupi."""

        if self._woupi_dialog is not None:

            try:

                if self._woupi_dialog.winfo_exists():
                    self._woupi_dialog.focus_force()
                    return

            except Exception:
                pass

            self._woupi_dialog = None

        def on_success():

            self.panel_log.add("OK", "log.woupi.connected")

            if connect_after and not self._closing:
                self.after(200, self._connect_now)

        self.panel_log.add("INFO", "log.woupi.account")

        self._woupi_dialog = WoupiAuthDialog(
            self,
            self.config,
            on_success=on_success
        )

    def on_disconnect(self):

        if self.app.connection:
            self.app.connection.stop()
            self.header.set_connection("disconnected")
            self.panel_log.add("INFO", "log.disconnected")

    def on_test_speak(self, text):

        self.app.tts.speak(text, username="Yo", display_name="Yo")

    def on_clear_queue(self):

        cleared = self.app.tts.clear_queue()

        self.header.set_queue(0)

        self.panel_log.add(
            "INFO", "log.queue.cleared", count=cleared
        )

    # ------------------------------------------------------------------ #

    def _load_voices(self, selected=None):

        if self._loading_voices:
            return

        provider = self.config.get("tts.provider")
        self._loading_voices = True

        def work():

            try:

                labels, values = _list_voices(provider)

            except Exception as exc:

                LoggerManager.logger.error(f"Voces: {exc}")

                labels, values = (
                    [i18n.t("voice.default")],
                    ["default"]
                )

            self._voice_results.put((provider, labels, values))

        threading.Thread(target=work, daemon=True, name="voice-loader").start()

    def _apply_voice_results(self):

        while True:

            try:

                provider, labels, values = self._voice_results.get_nowait()

            except queue.Empty:

                break

            self._loading_voices = False

            if provider != self.config.get("tts.provider"):
                continue

            self._voice_labels = labels
            self._voice_values = values

            self.panel_settings.set_voices(
                labels,
                self._voice_label_for(self.config.get("tts.voice"))
            )

    # ------------------------------------------------------------------ #
    # Eventos

    def _poll(self):

        if self._closing:
            return

        self.bridge.drain(self.on_event)

        self._apply_voice_results()

        self.after(80, self._poll)

    def on_event(self, name, data):

        data = data or {}

        if name == "connection.open":

            self.header.set_connection("connected")
            self.panel_log.add("OK", "log.ws.connected")

        elif name in ("connection.closed", "connection.missing_channel"):

            self.header.set_connection("disconnected")
            self.panel_log.add("AVISO", "log.ws.notconnected")

        elif name == "connection.error":

            self.header.set_connection("error")
            self.panel_log.add(
                "ERROR", "log.connection.error", error=data.get("error")
            )

        elif name == "chat.message":

            self.panel_log.write(
                "CHAT",
                f"{data.get('display_name') or data.get('username')}: "
                f"{data.get('text')}"
            )

        elif name == "tts.started":

            self.header.set_tts("active")

        elif name == "tts.stopped":

            self.header.set_tts("stopped")

        elif name == "tts.queued":

            self.header.set_queue(data.get("size", self.app.tts.pending))
            self.panel_log.add(
                "INFO", "log.queued",
                text=data.get("message", {}).get("text")
            )

        elif name == "tts.rejected":

            self.panel_log.add(
                "AVISO",
                "log.blocked",
                reason=data.get("reason"),
                text=data.get("message", {}).get("text")
            )

        elif name == "tts.speaking":

            text = data.get("message", {}).get("text", "")

            self.panel_log.add(
                "TTS",
                "log.speaking",
                text=f"{text[:120]}{'...' if len(text) > 120 else ''}"
            )
            self.header.set_queue(self.app.tts.pending)

        elif name == "tts.spoken":

            self.header.set_queue(data.get("size", self.app.tts.pending))

        elif name == "tts.queue.cleared":

            self.header.set_queue(0)

        elif name == "program.stopped":

            self.header.set_tts("stopped")
            self.header.set_connection("disconnected")

    # ------------------------------------------------------------------ #

    def refresh_plugin_status(self):

        plugins = self.app.plugins

        states = [p["state"] for p in plugins.describe()]

        if states:
            active = states.count("RUNNING")
            self.plugins_label.configure(
                text=i18n.t(
                    "log.plugins.loaded",
                    count=len(states),
                    active=active
                )
            )
        else:
            self.plugins_label.configure(text=i18n.t("log.plugins.none"))

    def _mark_dirty(self):

        self._dirty = True

        if self._save_job is not None:
            self.after_cancel(self._save_job)

        self._save_job = self.after(1200, self._save_now)

    def _save_now(self):

        self._save_job = None

        if self._dirty:

            try:

                self.app.config.save()

                self._dirty = False

            except Exception as exc:

                self.panel_log.add(
                    "ERROR", "log.save.error", error=exc
                )

    # ------------------------------------------------------------------ #

    def on_close(self):

        self._closing = True

        if self._save_job is not None:
            self.after_cancel(self._save_job)

        self._save_now()

        self.bridge.close()

        try:
            self.app.tts.stop()
        except Exception:
            pass

        try:
            if self.app.connection:
                self.app.connection.stop()
        except Exception:
            pass

        try:
            self.app.plugins.stop()
        except Exception:
            pass

        self.destroy()


def run_gui(app):
    """Crea y lanza la ventana (bloquea hasta cerrarla)."""

    window = VPZoneGUI(app)

    LoggerManager.logger.info("GUI iniciada")

    window.mainloop()