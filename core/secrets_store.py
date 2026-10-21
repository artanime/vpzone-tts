"""Almacenamiento seguro de credenciales.

Los secretos (api_key y tokens de Woupi) NO viven en
config/config.json. Se sirven de dos fuentes, ambas en .gitignore:

- Variables de entorno / ``.env``       → valores gestionados por el usuario.
- ``config/secrets.json``               → tokens generados por la app (OAuth).

Prioridad en la carga:

- ``api_key``: gana el entorno sobre el archivo.
- Tokens (access/refresh): gana ``secrets.json`` (la app los rota y los
  reescribe; el ``.env`` solo sirve como carga inicial).
"""

import json
import os

from core.paths import ENV_FILE, SECRETS_FILE

# clave de configuración → (variable de entorno, gana_el_entorno)
SECRET_FIELDS = {
    "api_key": ("VPZONE_API_KEY", True),
    "woupi.access_token": ("WOUPI_ACCESS_TOKEN", False),
    "woupi.refresh_token": ("WOUPI_REFRESH_TOKEN", False),
}

SECRET_KEYS = tuple(SECRET_FIELDS)


def is_secret(key):
    """¿Esta clave de configuración es un secreto?"""

    return key in SECRET_FIELDS


def load_env_file(path=None):
    """Carga el archivo ``.env`` en el entorno sin pisar variables ya definidas."""

    path = path or ENV_FILE

    try:
        raw = path.read_text(encoding="utf-8")

    except OSError:
        return

    for line in raw.splitlines():

        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        name, _, value = line.partition("=")

        name = name.strip()
        value = value.strip().strip('"').strip("'")

        if name and name not in os.environ:
            os.environ[name] = value


def env_secrets():
    """Secretos disponibles en variables de entorno."""

    result = {}

    for key, (env_name, _) in SECRET_FIELDS.items():

        value = (os.environ.get(env_name) or "").strip()

        if value:
            result[key] = value

    return result


def load_file_secrets():
    """Secretos persistidos por la app en ``config/secrets.json``."""

    try:
        raw = json.loads(SECRETS_FILE.read_text(encoding="utf-8"))

    except (OSError, ValueError):
        return {}

    if not isinstance(raw, dict):
        return {}

    result = {}

    for key in SECRET_FIELDS:

        value = str(raw.get(key) or "").strip()

        if value:
            result[key] = value

    return result


def save_file_secrets(values):
    """Escribe los secretos no vacíos en ``config/secrets.json``."""

    payload = {key: values[key] for key in SECRET_FIELDS if values.get(key)}

    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SECRETS_FILE, "w", encoding="utf-8") as f:

        json.dump(payload, f, indent=4, ensure_ascii=False)
