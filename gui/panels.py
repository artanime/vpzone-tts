"""Paneles de la interfaz de VPZone TTS."""

import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from core.constants import VERSION

from gui.i18n import LANGUAGE_NAMES, i18n

APP_ACCENT = "#7c5cff"
OK_COLOR = "#2fa75f"
WARN_COLOR = "#c7871a"
ERROR_COLOR = "#c23b3b"
IDLE_COLOR = "#4a4a55"

# Plataformas de chat disponibles (etiqueta mostrada -> código de config).
PLATFORM_NAMES = {
    "vpzone": "VPZone",
    "woupi": "Woupi"
}

PLATFORM_BY_NAME = {name: code for code, name in PLATFORM_NAMES.items()}

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "vpzone-mark.png"

LEVEL_COLORS = {
    "INFO": "#8f8fa8",
    "OK": OK_COLOR,
    "AVISO": WARN_COLOR,
    "ERROR": ERROR_COLOR,
    "CHAT": "#5ea8ff",
    "TTS": "#c9a7ff"
}


def stamp():

    return datetime.now().strftime("%H:%M:%S")


def load_logo(height=42):
    """Carga el logo del proyecto como CTkImage (mantiene proporción)."""

    try:

        from PIL import Image

        if not LOGO_PATH.exists():
            return None

        image = Image.open(LOGO_PATH)

        ratio = (image.width / image.height) if image.height else 1.0

        return ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(int(height * ratio), height)
        )

    except Exception:

        return None


class HeaderBar(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master, corner_radius=0, height=74, fg_color="#17171f")

        self._conn_state = "idle"
        self._tts_state = "idle"
        self._queue = 0
        self._provider = "-"

        self.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, rowspan=2, padx=(20, 24), pady=12, sticky="w")

        logo = load_logo()

        title_column = 0

        if logo is not None:

            ctk.CTkLabel(left, image=logo, text="").grid(
                row=0, column=0, padx=(0, 12)
            )

            title_column = 1

        title = ctk.CTkLabel(
            left,
            text="VPZone TTS",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=title_column, sticky="w")

        ctk.CTkLabel(
            left,
            text=f"v{VERSION}",
            font=ctk.CTkFont(size=11),
            text_color="#8f8fa8"
        ).grid(row=1, column=title_column, sticky="w", pady=(2, 0))

        self.connection = self._badge(self, "", IDLE_COLOR)
        self.connection.grid(row=0, column=1, padx=4, pady=(14, 2), sticky="w")

        self.tts = self._badge(self, "", IDLE_COLOR)
        self.tts.grid(row=1, column=1, padx=4, pady=(2, 14), sticky="w")

        self.queue = self._badge(self, "", IDLE_COLOR)
        self.queue.grid(row=0, column=2, padx=4, pady=(14, 2), sticky="e")

        self.provider = self._badge(self, "", IDLE_COLOR)
        self.provider.grid(row=1, column=2, padx=4, pady=(2, 14), sticky="e")

        self.grid_columnconfigure(2, weight=1)

        self.kofi_button = ctk.CTkButton(
            self,
            text="Ko-fi",
            width=64,
            height=28,
            corner_radius=8,
            fg_color="#ff5e5b",
            hover_color="#e04b48",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_kofi
        )
        self.kofi_button.grid(
            row=0, column=3, rowspan=2, padx=(8, 18), pady=12, sticky="e"
        )

        self.retranslate()

    @staticmethod
    def _badge(master, text, color):

        return ctk.CTkLabel(
            master,
            text=text,
            corner_radius=10,
            fg_color=color,
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=10,
            height=22,
            padx=10
        )

    @staticmethod
    def _open_kofi():

        try:
            webbrowser.open("https://ko-fi.com/artanime2")

        except Exception as exc:

            from core.logger_manager import LoggerManager

            LoggerManager.logger.warning(f"No se pudo abrir Ko-fi: {exc}")

    def set_connection(self, state):

        self._conn_state = state

        self._apply_connection()

    def set_tts(self, state):

        self._tts_state = state

        self._apply_tts()

    def set_queue(self, size, active=False):

        self._queue = size

        self._apply_queue(active)

    def set_provider(self, name):

        self._provider = name

        self._apply_provider()

    def _apply_connection(self):

        connected = self._conn_state == "connected"

        key = "header.connection.connected" if connected else (
            "header.connection.error"
            if self._conn_state == "error"
            else "header.connection.disconnected"
        )

        if connected:
            color = OK_COLOR
        elif self._conn_state == "idle":
            color = IDLE_COLOR
        else:
            color = ERROR_COLOR

        self.connection.configure(text=i18n.t(key), fg_color=color)

    def _apply_tts(self):

        active = self._tts_state == "active"

        if active:
            color = OK_COLOR
        elif self._tts_state == "idle":
            color = IDLE_COLOR
        else:
            color = WARN_COLOR

        self.tts.configure(
            text=i18n.t("header.tts.active" if active else "header.tts.stopped"),
            fg_color=color
        )

    def _apply_queue(self, active=False):

        self.queue.configure(
            text=i18n.t("header.queue", size=self._queue),
            fg_color=APP_ACCENT if active else IDLE_COLOR
        )

    def _apply_provider(self):

        self.provider.configure(
            text=i18n.t("header.provider", name=self._provider)
        )

    def retranslate(self):

        self._apply_connection()

        self._apply_tts()

        self._apply_queue()

        self._apply_provider()


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, master, callbacks):

        super().__init__(master, corner_radius=12, fg_color="#1d1d26")

        self.callbacks = callbacks

        self._volume_value = 100
        self._speed_value = 1.0

        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Título
        self.title_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        self.title_label.grid(row=row, column=0, sticky="ew", padx=14, pady=(14, 10))
        row += 1

        # Idioma
        self.language_label = ctk.CTkLabel(self, text="", anchor="w")
        self.language_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        self.language = ctk.CTkOptionMenu(
            self,
            values=list(LANGUAGE_NAMES.values()),
            command=lambda value: callbacks["language_changed"](value)
        )
        self.language.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        row += 1

        # Plataforma
        self.platform_label = ctk.CTkLabel(self, text="", anchor="w")
        self.platform_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        self.platform = ctk.CTkOptionMenu(
            self,
            values=list(PLATFORM_NAMES.values()),
            command=lambda value: callbacks["platform_changed"](value)
        )
        self.platform.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        row += 1

        # Canal
        self.channel_label = ctk.CTkLabel(self, text="", anchor="w")
        self.channel_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        channel_row = ctk.CTkFrame(self, fg_color="transparent")
        channel_row.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        channel_row.grid_columnconfigure(0, weight=1)
        row += 1

        self.channel = ctk.CTkEntry(channel_row)
        self.channel.grid(row=0, column=0, sticky="ew")

        self.apply_button = ctk.CTkButton(
            channel_row, text="", width=78,
            command=lambda: callbacks["apply_channel"](self.channel.get())
        )
        self.apply_button.grid(row=0, column=1, padx=(8, 0))

        # Proveedor
        self.provider_label = ctk.CTkLabel(self, text="", anchor="w")
        self.provider_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        self.provider = ctk.CTkOptionMenu(
            self,
            values=["..."],
            command=lambda value: callbacks["provider_changed"](value)
        )
        self.provider.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        row += 1

        # Voz
        self.voice_label = ctk.CTkLabel(self, text="", anchor="w")
        self.voice_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        voice_row = ctk.CTkFrame(self, fg_color="transparent")
        voice_row.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        voice_row.grid_columnconfigure(0, weight=1)
        row += 1

        self.voice = ctk.CTkOptionMenu(
            voice_row,
            values=["default"],
            command=lambda value: callbacks["voice_changed"](value)
        )
        self.voice.grid(row=0, column=0, sticky="ew")

        self.refresh_button = ctk.CTkButton(
            voice_row, text="", width=86,
            command=callbacks["refresh_voices"]
        )
        self.refresh_button.grid(row=0, column=1, padx=(8, 0))

        # Volumen
        self.volume_label = ctk.CTkLabel(self, text="", anchor="w")
        self.volume_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        self.volume = ctk.CTkSlider(
            self, from_=0, to=100, number_of_steps=100,
            command=self._on_volume
        )
        self.volume.set(100)
        self.volume.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        row += 1

        # Velocidad
        self.speed_label = ctk.CTkLabel(self, text="", anchor="w")
        self.speed_label.grid(row=row, column=0, sticky="w", padx=14)
        row += 1

        self.speed = ctk.CTkSlider(
            self, from_=0.5, to=2.0, number_of_steps=30,
            command=self._on_speed
        )
        self.speed.set(1.0)
        self.speed.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 10))
        row += 1

        # Leer usuario
        self.read_username = ctk.CTkSwitch(
            self,
            text="",
            command=self._on_read_username
        )
        self.read_username.grid(
            row=row, column=0, sticky="w", padx=14, pady=(0, 14)
        )
        row += 1

        # Acciones
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 14))
        actions.grid_columnconfigure((0, 1), weight=1)
        row += 1

        self.start_button = ctk.CTkButton(
            actions, text="", fg_color=OK_COLOR,
            hover_color="#268a4e",
            command=callbacks["start_tts"]
        )
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.stop_button = ctk.CTkButton(
            actions, text="", fg_color=ERROR_COLOR,
            hover_color="#a53131",
            command=callbacks["stop_tts"]
        )
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        connection = ctk.CTkFrame(self, fg_color="transparent")
        connection.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 14))
        connection.grid_columnconfigure((0, 1), weight=1)

        self.connect_button = ctk.CTkButton(
            connection, text="",
            command=callbacks["connect"]
        )
        self.connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.disconnect_button = ctk.CTkButton(
            connection, text="", fg_color="#3a3a45",
            hover_color="#2c2c34",
            command=callbacks["disconnect"]
        )
        self.disconnect_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        row += 1

        self.woupi_button = ctk.CTkButton(
            self, text="", fg_color="#3a3a45",
            hover_color="#2c2c34",
            command=callbacks["woupi_account"]
        )
        self.woupi_button.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 14))

        self.retranslate()

    def retranslate(self):

        self.title_label.configure(text=i18n.t("settings.title"))

        self.language_label.configure(text=i18n.t("settings.language"))

        self.platform_label.configure(text=i18n.t("settings.platform"))

        self.channel_label.configure(text=i18n.t("settings.channel"))

        self.channel.configure(
            placeholder_text=i18n.t("settings.channel.placeholder")
        )

        self.apply_button.configure(text=i18n.t("settings.apply"))

        self.provider_label.configure(text=i18n.t("settings.provider"))

        self.voice_label.configure(text=i18n.t("settings.voice"))

        self.refresh_button.configure(text=i18n.t("settings.refresh"))

        self.volume_label.configure(
            text=i18n.t("settings.volume", value=int(self._volume_value))
        )

        self.speed_label.configure(
            text=i18n.t("settings.speed", value=f"{self._speed_value:.2f}")
        )

        self.read_username.configure(text=i18n.t("settings.read_username"))

        self.start_button.configure(text=i18n.t("settings.start"))

        self.stop_button.configure(text=i18n.t("settings.stop"))

        self.connect_button.configure(text=i18n.t("settings.connect"))

        self.disconnect_button.configure(text=i18n.t("settings.disconnect"))

        self.woupi_button.configure(text=i18n.t("settings.woupi_account"))

        self.set_language(i18n.language)

    def set_language(self, code):

        self.language.set(LANGUAGE_NAMES.get(code, LANGUAGE_NAMES["es"]))

    def set_platform(self, code):

        self.platform.set(
            PLATFORM_NAMES.get((code or "vpzone").lower(), "VPZone")
        )

    def _on_volume(self, value):

        value = int(round(value))

        self._volume_value = value

        self.volume_label.configure(
            text=i18n.t("settings.volume", value=value)
        )

        self.callbacks["volume_changed"](value)

    def _on_speed(self, value):

        value = round(float(value), 2)

        self._speed_value = value

        self.speed_label.configure(
            text=i18n.t("settings.speed", value=f"{value:.2f}")
        )

        self.callbacks["speed_changed"](value)

    def _on_read_username(self):

        self.callbacks["read_username_changed"](
            bool(self.read_username.get())
        )

    # -------------------------------------------------------------- #

    def set_channel(self, value):

        self.channel.delete(0, "end")
        self.channel.insert(0, value or "")

    def set_providers(self, values, selected=None):

        values = values or ["debug"]

        self.provider.configure(values=values)

        if selected in values:
            self.provider.set(selected)

    def set_voices(self, values, selected=None):

        values = values or [i18n.t("voice.default")]

        self.voice.configure(values=values)

        if selected in values:
            self.voice.set(selected)
        else:
            self.voice.set(values[0])

    def set_values(self, channel=None, provider=None, voice=None,
                   volume=None, speed=None, read_username=None):

        if channel is not None:
            self.set_channel(channel)

        if provider is not None:
            self.provider.set(provider)

        if voice is not None:
            self.voice.set(voice)

        if volume is not None:

            self._volume_value = int(volume)

            self.volume.set(volume)

            self.volume_label.configure(
                text=i18n.t("settings.volume", value=int(volume))
            )

        if speed is not None:

            self._speed_value = round(float(speed), 2)

            self.speed.set(speed)

            self.speed_label.configure(
                text=i18n.t("settings.speed", value=f"{self._speed_value:.2f}")
            )

        if read_username is not None:
            if read_username:
                self.read_username.select()
            else:
                self.read_username.deselect()


class FiltersPanel(ctk.CTkFrame):

    FILTERS = [
        "length",
        "url",
        "emoji",
        "duplicate",
        "spam",
        "replace"
    ]

    def __init__(self, master, on_toggle):

        super().__init__(master, corner_radius=12, fg_color="#1d1d26")

        self.on_toggle = on_toggle

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.title_label.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 8)
        )

        self.switches = {}

        for index, key in enumerate(self.FILTERS):

            row = 1 + index // 2
            column = index % 2

            switch = ctk.CTkSwitch(
                self,
                text="",
                command=lambda k=key: self._toggle(k)
            )

            switch.grid(
                row=row, column=column,
                sticky="w", padx=14, pady=6
            )

            self.switches[key] = switch

        self.retranslate()

    def retranslate(self):

        self.title_label.configure(text=i18n.t("filters.title"))

        for key, switch in self.switches.items():

            switch.configure(text=i18n.t(f"filters.{key}"))

    def _toggle(self, key):

        enabled = bool(self.switches[key].get())

        self.on_toggle(f"tts.filters.{key}", enabled)

    def set_values(self, mapping):

        for key, switch in self.switches.items():

            if mapping.get(key):
                switch.select()
            else:
                switch.deselect()


class VoiceTestPanel(ctk.CTkFrame):

    def __init__(self, master, on_speak, on_clear):

        super().__init__(master, corner_radius=12, fg_color="#1d1d26")

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))
        row.grid_columnconfigure(0, weight=1)

        self.text = ctk.CTkEntry(row)
        self.text.grid(row=0, column=0, sticky="ew")
        self.text.bind("<Return>", lambda event: self._speak())

        self.speak_button = ctk.CTkButton(
            row, text="", width=80, fg_color=APP_ACCENT,
            command=self._speak
        )
        self.speak_button.grid(row=0, column=1, padx=(8, 0))

        self.clear_button = ctk.CTkButton(
            self, text="", width=110, fg_color="#3a3a45",
            hover_color="#2c2c34", command=on_clear
        )
        self.clear_button.grid(row=2, column=0, sticky="w", padx=14, pady=(0, 14))

        self.on_speak = on_speak

        self.retranslate()

    def retranslate(self):

        self.title_label.configure(text=i18n.t("test.title"))

        self.text.configure(placeholder_text=i18n.t("test.placeholder"))

        self.speak_button.configure(text=i18n.t("test.speak"))

        self.clear_button.configure(text=i18n.t("test.clear"))

    def _speak(self):

        text = self.text.get().strip()

        if not text:
            return

        self.on_speak(text)

        self.text.delete(0, "end")


class LogPanel(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master, corner_radius=12, fg_color="#1d1d26")

        # Historial de entradas para poder re-traducirlas al cambiar idioma.
        self._entries = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.clear_button = ctk.CTkButton(
            header, text="", width=80, fg_color="#3a3a45",
            hover_color="#2c2c34", command=self.clear
        )
        self.clear_button.grid(row=0, column=1, sticky="e")

        self.box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word",
            state="disabled"
        )
        self.box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        for level, color in LEVEL_COLORS.items():
            self.box.tag_config(level.lower(), foreground=color)

        self.retranslate()

    def retranslate(self):

        self.title_label.configure(text=i18n.t("log.title"))

        self.clear_button.configure(text=i18n.t("log.clear"))

        self._rerender()

    def write(self, level, message):
        """Escribe una línea ya formada (no traducible, p. ej. un chat)."""

        self._entries.append({
            "time": stamp(),
            "level": level if level in LEVEL_COLORS else "INFO",
            "text": message
        })

        self._render(self._entries[-1])

    def add(self, level, key, **kwargs):
        """Escribe una línea traducible por su clave i18n."""

        self._entries.append({
            "time": stamp(),
            "level": level if level in LEVEL_COLORS else "INFO",
            "key": key,
            "kwargs": kwargs
        })

        self._render(self._entries[-1])

    @staticmethod
    def _text(entry):

        if "key" in entry:
            return i18n.t(entry["key"], **entry.get("kwargs", {}))

        return entry.get("text", "")

    def _render(self, entry):

        self.box.configure(state="normal")

        self.box.insert(
            "end",
            f"[{entry['time']}] {self._text(entry)}\n",
            entry["level"].lower()
        )

        self.box.see("end")

        self.box.configure(state="disabled")

    def _rerender(self):

        self.box.configure(state="normal")

        self.box.delete("1.0", "end")

        for entry in self._entries:

            self.box.insert(
                "end",
                f"[{entry['time']}] {self._text(entry)}\n",
                entry["level"].lower()
            )

        self.box.see("end")

        self.box.configure(state="disabled")

    def clear(self):

        self._entries.clear()

        self.box.configure(state="normal")

        self.box.delete("1.0", "end")

        self.box.configure(state="disabled")
