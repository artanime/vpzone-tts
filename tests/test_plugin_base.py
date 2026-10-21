from runtime.plugin_base import PluginBase

plugin = PluginBase()

print(plugin.state)

plugin.initialize(None)

print(plugin.state)

plugin.start()

print(plugin.state)

plugin.stop()

print(plugin.state)

plugin.dispose()

print(plugin.state)