import importlib.util
from pathlib import Path


class ModuleResolver:

    def load(self, plugin_folder, manifest):

        plugin_folder = Path(plugin_folder)

        module_file = plugin_folder / manifest.entry

        if not module_file.exists():

            raise FileNotFoundError(module_file)

        module_name = f"plugins.{manifest.id}.plugin"

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_file
        )

        if spec is None or spec.loader is None:

            raise ImportError(
                f"No se pudo cargar {module_name}"
            )

        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        plugin_class = getattr(
            module,
            manifest.plugin_class
        )

        return plugin_class()