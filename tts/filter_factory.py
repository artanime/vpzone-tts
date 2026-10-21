from tts.filters.length_filter import LengthFilter
from tts.filters.url_filter import URLFilter
from tts.filters.emoji_filter import EmojiFilter
from tts.filters.duplicate_filter import DuplicateFilter
from tts.filters.spam_filter import SpamFilter


FILTERS = {
    "length": LengthFilter,
    "url": URLFilter,
    "emoji": EmojiFilter,
    "duplicate": DuplicateFilter,
    "spam": SpamFilter
}


class FilterFactory:

    @staticmethod
    def create(name):

        cls = FILTERS.get(name)

        if cls is None:
            return None

        return cls()