from tts.filter_manager import FilterManager
from tts.filter_factory import FilterFactory


class FilterRegistry:

    def __init__(self, config):

        self.config = config

    def build(self):

        manager = FilterManager()

        filters = self.config.get("tts.filters", {})

        for name, enabled in filters.items():

            if not enabled:
                continue

            filter_instance = FilterFactory.create(name)

            if filter_instance:

                manager.add(filter_instance)

        return manager
