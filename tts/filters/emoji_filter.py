import re

from tts.filters.base_filter import BaseFilter


class EmojiFilter(BaseFilter):

    EMOJIS = {
        "😀": " cara feliz ",
        "😁": " sonrisa ",
        "😂": " risas ",
        "🤣": " muchas risas ",
        "😊": " sonrisa ",
        "😍": " enamorado ",
        "😭": " llorando ",
        "😎": " genial ",
        "❤️": " corazón ",
        "💜": " corazón morado ",
        "👍": " pulgar arriba ",
        "👎": " pulgar abajo ",
        "🔥": " fuego ",
        "⭐": " estrella ",
        "✨": " brillo ",
        "🎉": " celebración ",
        "🎊": " fiesta ",
        "💯": " cien por cien "
    }

    def process(self, message):

        text = message.text

        for emoji, replacement in self.EMOJIS.items():
            text = text.replace(
                emoji,
                replacement
            )

        text = re.sub(r"\s+", " ", text)

        message.text = text.strip()

        return message