from runtime.core.plugin_manager import PluginManager
from runtime.context.plugin_context import PluginContext


class Runtime:

    def __init__(self):

        self.context = PluginContext()

        self.plugins = PluginManager()

    def initialize(self):

        self.plugins.initialize_all(

            self.context

        )

    def start(self):

        self.plugins.start_all()

    def stop(self):

        self.plugins.stop_all()

    def dispose(self):

        self.plugins.dispose_all()