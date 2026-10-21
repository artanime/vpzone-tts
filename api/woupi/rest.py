"""Cliente REST de la API de Woupi (https://api.woupi.buzz).

Implementa lo mínimo para el lector de chat:

- cabeceras ``Authorization: Bearer`` y ``Client-Id`` en cada petición;
- renovación automática del access token (``refresh_token``) ante un 401;
- reintento tras un 429 respetando ``Ratelimit-Reset``;
- ``validate`` (dueño del token), ``get_user_by_login`` y creación de la
  suscripción de EventSub.
"""

import time

import requests

from core.logger_manager import LoggerManager


API_BASE = "https://api.woupi.buzz"
TOKEN_URL = f"{API_BASE}/oauth2/token"
VALIDATE_URL = f"{API_BASE}/oauth2/validate"
DEVICE_URL = f"{API_BASE}/oauth2/device"

# Concesión del flujo de código de dispositivo (RFC 8628).
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


class WoupiError(Exception):
    """Error de la API de Woupi (respuesta no exitosa o token inválido)."""


class WoupiRestClient:
    """Cliente base para la API REST v1 de Woupi."""

    def __init__(self, client_id, access_token=None, refresh_token=None,
                 base_url=API_BASE, timeout=10):

        self.client_id = (client_id or "").strip()
        self.access_token = (access_token or "").strip() or None
        self.refresh_token = (refresh_token or "").strip() or None
        self.base_url = (base_url or API_BASE).rstrip("/")
        self.timeout = timeout

        # Callback opcional (access_token, refresh_token) que se llama cada
        # vez que se renueva el par, para que la app lo guarde en la config.
        self.on_tokens_refreshed = None

        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "VPZone-TTS/1.0"
        })

    # ------------------------------------------------------------------ #
    # Cabeceras

    def _headers(self, json_body=False):

        headers = {"Client-Id": self.client_id}

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        if json_body:
            headers["Content-Type"] = "application/json"

        return headers

    def _store_tokens(self, data):

        access = (data or {}).get("access_token")
        refresh = (data or {}).get("refresh_token")

        if access:
            self.access_token = str(access).strip()

        if refresh:
            self.refresh_token = str(refresh).strip()

        if self.on_tokens_refreshed:

            try:
                self.on_tokens_refreshed(self.access_token, self.refresh_token)

            except Exception as exc:

                LoggerManager.logger.error(
                    f"No se pudieron guardar los tokens de Woupi: {exc}"
                )

    # ------------------------------------------------------------------ #
    # OAuth

    def validate(self):
        """Comprueba el token y devuelve ``{login, user_id, scopes, ...}``."""

        if not self.access_token:
            return None

        try:

            response = self.session.get(
                VALIDATE_URL,
                headers={"Authorization": f"OAuth {self.access_token}"},
                timeout=self.timeout
            )

        except requests.RequestException as exc:

            LoggerManager.logger.error(f"Woupi validate: {exc}")

            return None

        if response.status_code != 200:

            LoggerManager.logger.warning(
                f"Woupi validate -> {response.status_code}"
            )

            return None

        try:
            return response.json()

        except ValueError:
            return None

    def refresh(self):
        """Renueva el access token con el refresh token. Devuelve bool."""

        if not (self.refresh_token and self.client_id):
            return False

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id
        }

        try:

            response = self.session.post(
                TOKEN_URL,
                data=payload,
                timeout=self.timeout
            )

        except requests.RequestException as exc:

            LoggerManager.logger.error(f"Woupi refresh: {exc}")

            return False

        if response.status_code != 200:

            LoggerManager.logger.warning(
                f"Woupi refresh -> {response.status_code}"
            )

            return False

        self._store_tokens(response.json())

        LoggerManager.logger.info("Token de Woupi renovado")

        return True

    # ------------------------------------------------------------------ #
    # Flujo de código de dispositivo (app pública, RFC 8628)

    def start_device_authorization(self, scopes=""):
        """Solicita un código de usuario para autorizar la app.

        Devuelve el JSON del servidor con ``device_code``, ``user_code``,
        ``verification_uri``, ``verification_uri_complete``, ``expires_in``
        e ``interval``. Lanza :class:`WoupiError` si falla.
        """

        if not self.client_id:
            raise WoupiError("Falta el client_id público de Woupi.")

        payload = {"client_id": self.client_id}

        if scopes:
            payload["scope"] = scopes

        try:

            response = self.session.post(
                DEVICE_URL,
                data=payload,
                timeout=self.timeout
            )

        except requests.RequestException as exc:

            LoggerManager.logger.error(f"Woupi device: {exc}")

            raise WoupiError(str(exc)) from exc

        if not response.ok:
            raise WoupiError(self._error_message(response))

        try:
            return response.json()

        except ValueError as exc:

            raise WoupiError(
                "Respuesta inválida del servidor de autorización."
            ) from exc

    def poll_device_token(self, device_code):
        """Intenta canjear el ``device_code``.

        Devuelve ``(status, data)`` donde ``status`` es ``"ok"``,
        ``"pending"``, ``"slow_down"``, ``"denied"``, ``"expired"`` o
        ``"error"``. Con ``"ok"`` los tokens ya quedan guardados.
        """

        payload = {
            "grant_type": DEVICE_GRANT,
            "device_code": device_code,
            "client_id": self.client_id
        }

        try:

            response = self.session.post(
                TOKEN_URL,
                data=payload,
                timeout=self.timeout
            )

        except requests.RequestException as exc:

            LoggerManager.logger.error(f"Woupi device poll: {exc}")

            raise WoupiError(str(exc)) from exc

        if response.status_code == 200:

            data = response.json()

            self._store_tokens(data)

            return ("ok", data)

        try:
            data = response.json()

        except ValueError:
            data = {}

        error = str(data.get("error") or "").lower()

        if error == "authorization_pending":
            return ("pending", data)

        if error == "slow_down":
            return ("slow_down", data)

        if error == "access_denied":
            return ("denied", data)

        if error == "expired_token":
            return ("expired", data)

        return ("error", data)

    def authorize_device(self, scopes="", on_code=None, is_cancelled=None):
        """Flujo completo (bloqueante): pide el código y espera aprobación.

        ``on_code`` recibe el dict del servidor en cuanto hay código (para
        mostrar el ``user_code``/``verification_uri``). ``is_cancelled`` es un
        callable opcional que, si devuelve ``True``, aborta la espera.

        Devuelve ``True`` si se autorizó. Lanza :class:`WoupiError` ante un
        error del servidor. Devuelve ``False`` si se canceló, se denegó o
        caducó el código.
        """

        info = self.start_device_authorization(scopes)

        device_code = info.get("device_code")

        if not device_code:
            raise WoupiError("El servidor no devolvió un device_code.")

        if on_code:

            try:
                on_code(info)

            except Exception as exc:

                LoggerManager.logger.error(f"Woupi on_code: {exc}")

        try:
            interval = max(int(info.get("interval") or 5), 1)

        except (TypeError, ValueError):
            interval = 5

        try:
            expires_in = int(info.get("expires_in") or 1800)

        except (TypeError, ValueError):
            expires_in = 1800

        deadline = time.time() + expires_in

        while time.time() < deadline:

            if is_cancelled and is_cancelled():
                return False

            status, data = self.poll_device_token(device_code)

            if status == "ok":
                return True

            if status == "pending":
                time.sleep(interval)

            elif status == "slow_down":
                interval += 5
                time.sleep(interval)

            elif status in ("denied", "expired"):
                return False

            else:

                raise WoupiError(
                    str(
                        (data or {}).get("error_description")
                        or (data or {}).get("error")
                        or "Error de autorización."
                    )
                )

        return False

    # ------------------------------------------------------------------ #
    # Peticiones

    def request(self, method, endpoint, params=None, json=None, retry=True):
        """Petición JSON autenticada. Lanza :class:`WoupiError` si falla."""

        url = self.base_url + endpoint

        try:

            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
                headers=self._headers(json_body=json is not None),
                timeout=self.timeout
            )

        except requests.RequestException as exc:

            LoggerManager.logger.error(f"Woupi {method} {endpoint}: {exc}")

            raise WoupiError(str(exc)) from exc

        # Token caducado: renovar y reintentar una vez.
        if response.status_code == 401 and retry and self.refresh_token:

            if self.refresh():

                return self.request(
                    method, endpoint,
                    params=params, json=json, retry=False
                )

        # Límite de peticiones: esperar al reset y reintentar una vez.
        if response.status_code == 429 and retry:

            self._wait_rate_limit(response)

            return self.request(
                method, endpoint,
                params=params, json=json, retry=False
            )

        LoggerManager.logger.info(
            f"Woupi {method} {endpoint} -> {response.status_code}"
        )

        if not response.ok:
            raise WoupiError(self._error_message(response))

        if response.status_code == 204 or not response.content:
            return {}

        try:
            return response.json()

        except ValueError:
            return {}

    @staticmethod
    def _wait_rate_limit(response):

        reset = response.headers.get("Ratelimit-Reset")

        try:
            wait = max(int(reset) - int(time.time()), 1) if reset else 5

        except (TypeError, ValueError):
            wait = 5

        wait = min(wait, 60)

        LoggerManager.logger.warning(
            f"Woupi: límite de peticiones alcanzado, esperando {wait}s"
        )

        time.sleep(wait)

    @staticmethod
    def _error_message(response):

        try:
            data = response.json()

        except ValueError:
            return f"HTTP {response.status_code}"

        message = data.get("message") or data.get("error") or ""

        return f"HTTP {response.status_code}: {message}".strip()

    # ------------------------------------------------------------------ #
    # Endpoints usados por el lector de chat

    def get_user_by_login(self, login):
        """Devuelve el usuario (``{id, login, ...}``) de un canal o ``None``."""

        login = (login or "").strip()

        if not login:
            return None

        data = self.request("GET", "/v1/users", params={"login": login})

        users = (data or {}).get("data") or []

        return users[0] if users else None

    def send_chat_message(self, broadcaster_id, message):
        """Envía un mensaje al chat (scope ``chat:write``)."""

        return self.request("POST", "/v1/chat/messages", json={
            "broadcaster_id": str(broadcaster_id),
            "message": message
        })

    def create_eventsub_subscription(self, event_type, version, condition,
                                     transport):
        """Crea una suscripción de EventSub (WebSocket o webhook)."""

        return self.request("POST", "/v1/eventsub/subscriptions", json={
            "type": event_type,
            "version": version,
            "condition": condition,
            "transport": transport
        })
