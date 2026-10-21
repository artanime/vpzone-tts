import importlib
import pkgutil

import tts.providers

from core.logger_manager import LoggerManager


class ProviderLoader:

    _loaded = False
    _failed = []

    @classmethod
    def load(cls):
        """Importa todos los proveedores del paquete para que se registren."""

        if cls._loaded:
            return list(cls._failed)

        package = tts.providers

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):

            try:

                importlib.import_module(
                    f"tts.providers.{module_name}"
                )

            except Exception as exc:

                cls._failed.append(module_name)

                LoggerManager.logger.warning(
                    f"No se pudo cargar el proveedor '{module_name}': {exc}"
                )

        cls._loaded = True

        return list(cls._failed)

    @classmethod
    def failed(cls):

        return list(cls._failed)
