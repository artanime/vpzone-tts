from runtime.core.plugin_loader import PluginLoader

loader = PluginLoader()

print("Carpeta plugins:", loader.plugins_folder)

plugins = loader.discover()

print("Plugins encontrados:", len(plugins))

for plugin in plugins:
    print(plugin.name)
