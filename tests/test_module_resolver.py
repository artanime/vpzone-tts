from runtime.core.plugin_loader import PluginLoader

loader = PluginLoader()

plugins = loader.load_all()

print("Plugins cargados:", len(plugins))

for plugin in plugins:

    print(type(plugin).__name__)