from tts.provider_factory import ProviderFactory
from tts.provider_loader import ProviderLoader


class VoiceManager:

    def __init__(self, config):

        self.config = config

        # Cargar automáticamente todos los proveedores
        ProviderLoader.load()

    def provider(self):
        """Instancia el proveedor configurado; si no existe, el mejor disponible."""

        provider_name = self.config.get("tts.provider", "debug")

        if not ProviderFactory.exists(provider_name):

            available = ProviderFactory.names()

            if available:
                provider_name = available[0]

        try:

            return ProviderFactory.create(provider_name, self.config)

        except Exception:

            return ProviderFactory.create("debug", self.config)

    def set_provider(self, name):

        self.config.set("tts.provider", name, autosave=True)

    @staticmethod
    def names():

        ProviderLoader.load()

        return ProviderFactory.names()

    @staticmethod
    def infos():

        ProviderLoader.load()

        return ProviderFactory.providers()
