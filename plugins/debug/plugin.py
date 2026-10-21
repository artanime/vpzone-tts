from runtime.plugin_base import PluginBase


class DebugPlugin(PluginBase):

    def initialize(self, context):

        super().initialize(context)

        print("DebugPlugin inicializado")

    def start(self):

        super().start()

        print("DebugPlugin iniciado")

    def stop(self):

        super().stop()

        print("DebugPlugin detenido")