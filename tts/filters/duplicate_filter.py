import time

from tts.filters.base_filter import BaseFilter


class DuplicateFilter(BaseFilter):

    def __init__(self, seconds=10):

        self.seconds = seconds

        self.cache = {}

    def process(self, message):

        now = time.time()

        key = (
            message.username,
            message.text.lower()
        )

        if key in self.cache:

            last = self.cache[key]

            if now - last < self.seconds:

                return None

        self.cache[key] = now

        return message