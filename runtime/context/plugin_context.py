class PluginContext:

    def __init__(
        self,
        config=None,
        events=None,
        logger=None,
        services=None,
        providers=None,
        filters=None,
        runtime=None,
        scheduler=None
    ):

        self.config = config

        self.events = events

        self.logger = logger

        self.services = services

        self.providers = providers

        self.filters = filters

        self.runtime = runtime

        self.scheduler = scheduler
