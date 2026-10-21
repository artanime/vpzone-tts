import re

from tts.filters.base_filter import BaseFilter


class URLFilter(BaseFilter):

    URL_PATTERN = re.compile(
        r"(https?://\S+|www\.\S+)",
        re.IGNORECASE
    )

    def __init__(self, replace_with="enlace"):

        self.replace_with = replace_with

    def process(self, message):

        message.text = self.URL_PATTERN.sub(
            self.replace_with,
            message.text
        )

        return message