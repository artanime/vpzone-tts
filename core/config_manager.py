import copy
import json

from core.paths import CONFIG_FILE
from core import secrets_store
from config.defaults import DEFAULT_CONFIG


class ConfigManager:

    def __init__(self):

        self.data = copy.deepcopy(DEFAULT_CONFIG)
        self._path = CONFIG_FILE

    def load(self):

        secrets_store.load_env_file()

        stored = {}

        if self._path.exists():

            with open(self._path, "r", encoding="utf-8") as f:

                stored = json.load(f)

        # Migración: si un config.json antiguo todavía guardaba secretos,
        # se extraen y se reescribe el archivo limpio.
        migrated = {}

        for key in secrets_store.SECRET_KEYS:

            value = self._extract(stored, key)

            if value:
                migrated[key] = value

        self.data = self._merge(copy.deepcopy(DEFAULT_CONFIG), stored)

        file_secrets = {**migrated, **secrets_store.load_file_secrets()}
        env = secrets_store.env_secrets()

        for key in secrets_store.SECRET_KEYS:

            env_wins = secrets_store.SECRET_FIELDS[key][1]

            if env_wins:
                value = env.get(key) or file_secrets.get(key, "")
            else:
                value = file_secrets.get(key) or env.get(key, "")

            if value:
                self.set(key, value)

        if migrated:
            self.save()

        return self.data

    def save(self):

        self._path.parent.mkdir(parents=True, exist_ok=True)

        clean = copy.deepcopy(self.data)
        secrets = {}

        for key in secrets_store.SECRET_KEYS:

            value = self._extract(clean, key)

            if value:
                secrets[key] = value

        with open(self._path, "w", encoding="utf-8") as f:

            json.dump(clean, f, indent=4, ensure_ascii=False)

        secrets_store.save_file_secrets(secrets)

    def get(self, key, default=None):

        value = self.data

        for part in key.split("."): 

            if not isinstance(value, dict) or part not in value:
                return default

            value = value[part]

        return value

    def set(self, key, value, autosave=False):

        parts = key.split(".")

        target = self.data

        for part in parts[:-1]:

            if not isinstance(target.get(part), dict):
                target[part] = {}

            target = target[part]

        target[parts[-1]] = value

        if autosave:
            self.save()

        return value

    @staticmethod
    def _merge(base, override):

        result = dict(base)

        for key, value in override.items():

            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = ConfigManager._merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def _extract(data, key):
        """Extrae (y elimina) una clave anidada; devuelve texto plano o ""."""

        parts = key.split(".")

        target = data

        for part in parts[:-1]:

            if not isinstance(target.get(part), dict):
                return ""

            target = target[part]

        value = target.pop(parts[-1], "")

        if value is None:
            return ""

        return str(value).strip()
