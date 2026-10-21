from tts.filters.base_filter import BaseFilter


class LengthFilter(BaseFilter):

    def __init__(self, max_length=250):
        self.max_length = max_length

    def process(self, message):

        if len(message.text) > self.max_length:
            return None

        return message