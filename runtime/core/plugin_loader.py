from pathlib import Path

from core.logger_manager import LoggerManager
from core.paths import PLUGIN_DIR
from runtime.context.plugin_manifest import PluginManifest
from runtime.core.module_resolver import ModuleResolver


class PluginLoader:

    def __init__(self, plugins_folder=PLUGIN_DIR):

        self.plugins_folder = Path(plugins_folder)

        self.resolver = ModuleResolver()

        # Errores por carpeta de plugin (clave: nombre de la carpeta)
        self.errors = {}

    def discover(self):

        manifests = []

        self.errors = {}

        if not self.plugins_folder.exists():
            return manifests

        for folder in sorted(self.plugins_folder.iterdir()):

            if not folder.is_dir():
                continue

            manifest = folder / "plugin.json"

            if not manifest.exists():
                continue

            try:

                manifests.append(
                    PluginManifest.from_file(manifest)
                )

            except Exception as exc:

                self.errors[folder.name] = str(exc)

                LoggerManager.logger.warning(
                    f"Plugin '{folder.name}': manifiesto inválido: {exc}"
                )

        return manifests

    def load_all(self):

        plugins = []

        self.errors = {}

        if not self.plugins_folder.exists():

            LoggerManager.logger.warning(
                f"No existe la carpeta de plugins: {self.plugins_folder}"
            )

            return plugins

        for folder in sorted(self.plugins_folder.iterdir()):

            if not folder.is_dir():
                continue

            manifest_file = folder / "plugin.json"

            if not manifest_file.exists():
                continue

            try:

                manifest = PluginManifest.from_file(manifest_file)

                plugins.append(
                    self.resolver.load(folder, manifest)
                )

            except Exception as exc:

                self.errors[folder.name] = str(exc)

                LoggerManager.logger.warning(
                    f"Plugin '{folder.name}': no se pudo cargar: {exc}"
                )

        return plugins

    def manifests(self):
        """Lista de (carpeta, manifiesto) para mostrar en la interfaz."""

        result = []

        for manifest in self.discover():
            result.append(manifest)

        return result
