from runtime.context.plugin_context import PluginContext

context = PluginContext()

print(context.config)
print(context.events)
print(context.logger)
print(context.services)
print(context.providers)
print(context.filters)
print(context.runtime)
print(context.scheduler)
