class ProviderInfo:

    def __init__(
        self,
        name,
        provider,
        version="1.0.0",
        author="Unknown",
        description="",
        local=True,
        cloud=False,
        gpu=False,
        languages=None,
        priority=0,
        capabilities=None
    ):

        self.name = name
        self.provider = provider

        self.version = version
        self.author = author
        self.description = description

        self.local = local
        self.cloud = cloud
        self.gpu = gpu

        self.languages = languages or []

        self.priority = priority

        self.capabilities = capabilities or []
