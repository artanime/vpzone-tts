"""Asistente de autorización de Woupi (flujo de código de dispositivo).

Permite al usuario autorizar la aplicación en su propia cuenta de Woupi sin
que el programa maneje contraseñas ni secretos: solo se usa el ``client_id``
público y el flujo de código de dispositivo (RFC 8628). Los tokens resultantes
se guardan en la configuración local del usuario.
"""

import threading
import webbrowser

import customtkinter as ctk

from core.constants import WOUPI_CLIENT_ID, WOUPI_SCOPES
from core.logger_manager import LoggerManager

from api.woupi.rest import WoupiError, WoupiRestClient

from gui.i18n import i18n

from gui.panels import APP_ACCENT, ERROR_COLOR, OK_COLOR


class WoupiAuthDialog(ctk.CTkToplevel):
    """Diálogo modal para autorizar Woupi mediante código de dispositivo."""

    def __init__(self, master, config, on_success=None):

        super().__init__(master)

        self.config = config
        self.on_success = on_success

        self._client = None
        self._cancelled = False
        self._running = False
        self._code_info = None

        self.title(i18n.t("woupi.title"))
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(master)

        self.grid_columnconfigure(0, weight=1)

        row = 0

        self.title_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=17, weight="bold"), anchor="w"
        )
        self.title_label.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 8))
        row += 1

        self.intro_label = ctk.CTkLabel(
            self, text="", anchor="w", justify="left", wraplength=440
        )
        self.intro_label.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 14))
        row += 1

        self.client_label = ctk.CTkLabel(self, text="", anchor="w")
        self.client_label.grid(row=row, column=0, sticky="w", padx=20)
        row += 1

        self.client_entry = ctk.CTkEntry(self)
        self.client_entry.grid(
            row=row, column=0, sticky="ew", padx=20, pady=(0, 14)
        )
        row += 1

        self.connect_button = ctk.CTkButton(
            self, text="", fg_color=APP_ACCENT, command=self._start
        )
        self.connect_button.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
        row += 1

        self.code_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.code_label.grid(row=row, column=0, sticky="ew", padx=20, pady=(4, 2))
        row += 1

        self.browser_button = ctk.CTkButton(
            self, text="", fg_color="#3a3a45", hover_color="#2c2c34",
            command=self._open_browser
        )
        self.browser_button.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
        row += 1

        self.status_label = ctk.CTkLabel(
            self, text="", anchor="w", justify="left", wraplength=440
        )
        self.status_label.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
        row += 1

        self.close_button = ctk.CTkButton(
            self, text="", fg_color="#3a3a45", hover_color="#2c2c34",
            command=self._on_close
        )
        self.close_button.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 20))

        self._hide_code()

        self.retranslate()

        self.client_entry.insert(0, self._current_client_id())

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.after(80, self._activate)

    # ------------------------------------------------------------------ #

    def _activate(self):

        try:
            self.grab_set()
            self.focus_force()

        except Exception:
            pass

    def _call_ui(self, func, *args):
        """Programa una actualización de la UI desde el hilo de red.

        Silencioso si el diálogo ya se cerró (el usuario lo cerró mientras
        esperábamos) para no dejar excepciones en el hilo de fondo.
        """

        if self._cancelled:
            return

        try:

            if not self.winfo_exists():
                return

            self.after(0, func, *args)

        except Exception:
            pass

    def _current_client_id(self):

        return (
            (self.config.get("woupi.client_id") or "").strip()
            or WOUPI_CLIENT_ID
        )

    def _scopes(self):

        return (self.config.get("woupi.scopes") or WOUPI_SCOPES).strip()

    def retranslate(self):

        self.title_label.configure(text=i18n.t("woupi.title"))
        self.intro_label.configure(text=i18n.t("woupi.intro"))
        self.client_label.configure(text=i18n.t("woupi.client_id"))
        self.client_entry.configure(
            placeholder_text=i18n.t("woupi.client_id.placeholder")
        )
        self.connect_button.configure(text=i18n.t("woupi.connect"))
        self.browser_button.configure(text=i18n.t("woupi.open_browser"))
        self.close_button.configure(text=i18n.t("woupi.close"))

        if self._code_info:
            self.code_label.configure(
                text=f"{i18n.t('woupi.code')} {self._code_info.get('user_code', '')}"
            )

    def _hide_code(self):

        self.code_label.grid_remove()
        self.browser_button.grid_remove()

    def _show_code(self, info):

        self._code_info = info

        self.code_label.configure(
            text=f"{i18n.t('woupi.code')} {info.get('user_code', '')}"
        )
        self.code_label.grid()
        self.browser_button.grid()

    def _set_status(self, text, color=None):

        self.status_label.configure(text=text)

        if color is not None:
            self.status_label.configure(text_color=color)

    # ------------------------------------------------------------------ #

    def _start(self):

        if self._running:
            return

        client_id = self.client_entry.get().strip()

        if not client_id:

            self._set_status(i18n.t("woupi.missing_client"), ERROR_COLOR)

            return

        self.config.set("woupi.client_id", client_id)

        self._client = WoupiRestClient(
            client_id=client_id,
            base_url=self.config.get("woupi.api_base_url")
        )

        self._cancelled = False
        self._running = True

        self.connect_button.configure(state="disabled")
        self.client_entry.configure(state="disabled")

        self._set_status(i18n.t("woupi.waiting"), None)

        threading.Thread(
            target=self._worker,
            name="woupi-device-auth",
            daemon=True
        ).start()

    def _worker(self):

        try:

            ok = self._client.authorize_device(
                scopes=self._scopes(),
                on_code=lambda info: self._call_ui(self._on_code, info),
                is_cancelled=lambda: self._cancelled
            )

        except WoupiError as exc:

            self._call_ui(self._on_error, str(exc))
            return

        except Exception as exc:

            LoggerManager.logger.error(f"Woupi device auth: {exc}")
            self._call_ui(self._on_error, str(exc))
            return

        self._call_ui(self._on_result, ok)

    def _on_code(self, info):

        if self._cancelled:
            return

        self._show_code(info)

        url = info.get("verification_uri_complete") or info.get("verification_uri")

        if url:
            self._open_url(url)

    def _open_browser(self):

        if not self._code_info:
            return

        url = (
            self._code_info.get("verification_uri_complete")
            or self._code_info.get("verification_uri")
        )

        if url:
            self._open_url(url)

    @staticmethod
    def _open_url(url):

        try:
            webbrowser.open(url)

        except Exception as exc:

            LoggerManager.logger.warning(f"No se pudo abrir el navegador: {exc}")

    def _on_result(self, ok):

        self._running = False

        if ok:

            self._persist_tokens()

            self._set_status(i18n.t("woupi.success"), OK_COLOR)

            self.connect_button.configure(state="normal")
            self.client_entry.configure(state="normal")

            if self.on_success:
                self.on_success()

            self.after(900, self._on_close)

            return

        if self._cancelled:
            return

        self._set_status(i18n.t("woupi.error", error=""), ERROR_COLOR)

        self.connect_button.configure(state="normal")
        self.client_entry.configure(state="normal")

    def _on_error(self, message):

        self._running = False

        self._set_status(i18n.t("woupi.error", error=message), ERROR_COLOR)

        self.connect_button.configure(state="normal")
        self.client_entry.configure(state="normal")

    def _persist_tokens(self):

        if not self._client:
            return

        if self._client.access_token:
            self.config.set("woupi.access_token", self._client.access_token)

        if self._client.refresh_token:
            self.config.set("woupi.refresh_token", self._client.refresh_token)

        try:
            self.config.save()

        except Exception as exc:

            LoggerManager.logger.error(
                f"No se pudieron guardar los tokens de Woupi: {exc}"
            )

    def _on_close(self):

        self._cancelled = True

        try:
            self.grab_release()

        except Exception:
            pass

        self.destroy()
