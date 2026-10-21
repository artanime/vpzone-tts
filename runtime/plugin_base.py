from runtime.lifecycle.plugin_state import PluginState


class PluginBase:

    def __init__(self):

        self.context = None

        self.state = PluginState.DISCOVERED

    def initialize(self, context):

        self.context = context

        self.state = PluginState.INITIALIZED

    def start(self):

        self.state = PluginState.STARTED

    def stop(self):

        self.state = PluginState.STOPPED

    def dispose(self):

        self.state = PluginState.UNLOADED
