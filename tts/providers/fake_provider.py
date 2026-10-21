from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory
from tts.capabilities import Capability


class FakeProvider(BaseProvider):

    name = "fake"

    def speak(self, text):
        print("Fake:", text)


ProviderFactory.register(

    name="fake",

    provider=FakeProvider,

    version="1.0.0",

    author="VPZone",

    description="Proveedor falso (solo texto)",

    local=True,

    cloud=False,

    gpu=False,

    languages=["*"],

    priority=0,

    capabilities=[Capability.LOCAL, Capability.OFFLINE]
)
