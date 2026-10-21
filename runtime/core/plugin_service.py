from core.logger_manager import LoggerManager
from core.paths import PLUGIN_DIR
from runtime.context.plugin_context import PluginContext
from runtime.core.plugin_loader import PluginLoader
from runtime.core.plugin_manager import PluginManager
from runtime.lifecycle.plugin_state import PluginState


class PluginService:
    """Carga los plugins de la carpeta `plugins/` y gestiona su ciclo de vida.

    Se registra en el `ServiceManager` como cualquier otro servicio.
    """

    def __init__(self, config=None, events=None, services=None,
                 providers=None, filters=None):

        self.loader = PluginLoader(PLUGIN_DIR)

        self.manager = PluginManager()

        self.context = PluginContext(
            config=config,
            events=events,
            logger=LoggerManager.logger,
            services=services,
            providers=providers,
            filters=filters,
            runtime=self
        )

        self.loaded = False

    def start(self):

        plugins = self.loader.load_all()

        for plugin in plugins:
            self.manager.add(plugin)

        self.manager.initialize_all(self.context)

        self.manager.start_all()

        self.loaded = True

        for name, error in self.loader.errors.items():

            LoggerManager.logger.error(f"Plugin '{name}': {error}")

        LoggerManager.logger.info(
            f"Plugins: {len(self.manager.get_plugins())} cargados, "
            f"{len(self.manager.running())} activos"
        )

    def stop(self):

        if not self.loaded:
            return

        self.manager.stop_all()

        self.manager.dispose_all()

        self.loaded = False

    def describe(self):
        """Estado de cada plugin para mostrarlo en la interfaz."""

        result = []

        for plugin in self.manager.get_plugins():

            manifest = getattr(plugin, "manifest", None)

            result.append({
                "id": getattr(manifest, "id", type(plugin).__name__),
                "name": getattr(manifest, "name", type(plugin).__name__),
                "state": plugin.state.name,
                "error": self.manager.errors.get(plugin, "")
            })

        for name, error in self.loader.errors.items():

            result.append({
                "id": name,
                "name": name,
                "state": PluginState.ERROR.name,
                "error": error
            })

        return result

    @property
    def active(self):

        return len(self.manager.running())
