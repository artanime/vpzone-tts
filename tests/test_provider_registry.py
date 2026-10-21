from tts.provider_factory import ProviderFactory

import tts.providers.debug_provider


print("=" * 50)

for provider in ProviderFactory.providers():

    print("Nombre      :", provider.name)
    print("Autor       :", provider.author)
    print("Versión     :", provider.version)
    print("Descripción :", provider.description)
    print("Local       :", provider.local)
    print("Cloud       :", provider.cloud)
    print("GPU         :", provider.gpu)
    print("Idiomas     :", provider.languages)
    print("Prioridad   :", provider.priority)

    print("-" * 50)