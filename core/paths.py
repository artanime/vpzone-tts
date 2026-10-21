"""Rutas absolutas del proyecto.

Todas las rutas se resuelven a partir de la raíz del proyecto para que la
aplicación funcione independientemente del directorio de trabajo actual.
"""

from pathlib import Path

import shutil

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Secretos (ambos en .gitignore; ver core/secrets_store.py)
ENV_FILE = BASE_DIR / ".env"
SECRETS_FILE = CONFIG_DIR / "secrets.json"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

VOICE_DIR = BASE_DIR / "voices"
AUDIO_DIR = BASE_DIR / "audio"
TEMP_DIR = BASE_DIR / "temp"
PLUGIN_DIR = BASE_DIR / "plugins"

FOLDERS = [
    LOG_DIR,
    VOICE_DIR,
    AUDIO_DIR,
    TEMP_DIR,
    PLUGIN_DIR,
]


def path(*parts):
    """Devuelve una ruta absoluta dentro del proyecto."""

    return BASE_DIR.joinpath(*parts)


def ensure_folders():
    """Crea las carpetas requeridas si no existen."""

    for folder in FOLDERS:
        folder.mkdir(parents=True, exist_ok=True)


def purge_temp():
    """Elimina todo el contenido de la carpeta temporal.

    Devuelve el número de elementos borrados. Ignora los archivos en uso
    (por ejemplo, un audio reproduciéndose en Windows).
    """

    if not TEMP_DIR.exists():
        return 0

    removed = 0

    for item in TEMP_DIR.iterdir():

        try:

            if item.is_dir() and not item.is_symlink():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink()

            removed += 1

        except OSError:
            continue

    return removed
