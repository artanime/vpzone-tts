from tts.providers.base_provider import BaseProvider
from tts.provider_factory import ProviderFactory
from tts.capabilities import Capability


class DebugProvider(BaseProvider):

    name = "debug"

    def load(self):
        print("[DEBUG] Provider cargado")

    def speak(self, text):
        print(f"[DEBUG] {text}")

    def stop(self):
        print("[DEBUG] Stop")

    def close(self):
        print("[DEBUG] Close")


ProviderFactory.register(

    name="debug",

    provider=DebugProvider,

    version="1.0.0",

    author="VPZone",

    description="Proveedor de depuración",

    local=True,

    cloud=False,

    gpu=False,

    languages=["*"],

    priority=1,

    capabilities=[
        Capability.LOCAL,
        Capability.OFFLINE,
        Capability.FAST
    ]
)
