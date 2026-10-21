from core.logger_manager import LoggerManager
from runtime.lifecycle.plugin_state import PluginState


class PluginManager:

    def __init__(self):

        self.plugins = []

        self.errors = {}

    def add(self, plugin):

        self.plugins.append(plugin)

    def initialize_all(self, context):

        for plugin in self.plugins:

            if plugin.state == PluginState.ERROR:
                continue

            try:

                plugin.initialize(context)

            except Exception as exc:

                plugin.state = PluginState.ERROR

                self.errors[plugin] = str(exc)

                LoggerManager.logger.exception(
                    f"Plugin {type(plugin).__name__}: initialize falló: {exc}"
                )

    def start_all(self):

        for plugin in self.plugins:

            if plugin.state == PluginState.ERROR:
                continue

            try:

                plugin.start()

                if plugin.state != PluginState.ERROR:
                    plugin.state = PluginState.RUNNING

            except Exception as exc:

                plugin.state = PluginState.ERROR

                self.errors[plugin] = str(exc)

                LoggerManager.logger.exception(
                    f"Plugin {type(plugin).__name__}: start falló: {exc}"
                )

    def stop_all(self):

        for plugin in self.plugins:

            if plugin.state != PluginState.RUNNING:
                continue

            try:

                plugin.state = PluginState.STOPPING

                plugin.stop()

                if plugin.state not in (PluginState.ERROR, PluginState.STOPPED):
                    plugin.state = PluginState.STOPPED

            except Exception as exc:

                plugin.state = PluginState.ERROR

                self.errors[plugin] = str(exc)

                LoggerManager.logger.exception(
                    f"Plugin {type(plugin).__name__}: stop falló: {exc}"
                )

    def dispose_all(self):

        for plugin in self.plugins:

            try:

                plugin.dispose()

            except Exception as exc:

                plugin.state = PluginState.ERROR

                self.errors[plugin] = str(exc)

                LoggerManager.logger.exception(
                    f"Plugin {type(plugin).__name__}: dispose falló: {exc}"
                )

    def get_plugins(self):

        return self.plugins

    def running(self):

        return [

            plugin

            for plugin in self.plugins

            if plugin.state == PluginState.RUNNING

        ]

    def failed(self):

        return [

            plugin

            for plugin in self.plugins

            if plugin.state == PluginState.ERROR

        ]
