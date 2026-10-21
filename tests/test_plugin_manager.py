from runtime.core.plugin_manager import PluginManager
from runtime.plugin_base import PluginBase
from runtime.context.plugin_context import PluginContext


manager = PluginManager()

plugin = PluginBase()

manager.add(plugin)

context = PluginContext()

manager.initialize_all(context)

manager.start_all()

print(plugin.state)

manager.stop_all()

print(plugin.state)

manager.dispose_all()

print(plugin.state)