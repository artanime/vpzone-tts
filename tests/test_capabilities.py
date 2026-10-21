from tts.provider_factory import ProviderFactory
from tts.capabilities import Capability

# Importar proveedores para que se registren
import tts.providers.debug_provider

print("=" * 50)
print("Proveedores OFFLINE")
print("=" * 50)

for provider in ProviderFactory.find_by_capability(
    Capability.OFFLINE
):

    print(provider.name)