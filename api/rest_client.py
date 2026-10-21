import requests
from requests.exceptions import RequestException

from core.logger_manager import LoggerManager


class RestClient:
    """
    Cliente base para la API REST de VPZone.
    """

    def __init__(self, base_url: str, api_key: str | None = None, timeout: int = 10):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "VPZone-TTS/1.0"
        })

        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })

    def get(self, endpoint, params=None):

        return self._request(
            "GET",
            endpoint,
            params=params
        )

    def post(self, endpoint, json=None):

        return self._request(
            "POST",
            endpoint,
            json=json
        )

    def put(self, endpoint, json=None):

        return self._request(
            "PUT",
            endpoint,
            json=json
        )

    def delete(self, endpoint):

        return self._request(
            "DELETE",
            endpoint
        )

    def _request(self, method, endpoint, **kwargs):

        url = self.base_url + endpoint

        try:

            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )

            response.raise_for_status()

            LoggerManager.logger.info(
                f"{method} {endpoint} -> {response.status_code}"
            )

            if response.content:
                return response.json()

            return {}

        except RequestException as e:

            LoggerManager.logger.error(str(e))

            print(f"[REST ERROR] {e}")

            return None