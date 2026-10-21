import re

from tts.filters.base_filter import BaseFilter


class SpamFilter(BaseFilter):

    def __init__(self):

        self.max_repeated_chars = 8

    def process(self, message):

        text = message.text.strip()

        # Mensaje vacío
        if not text:
            return None

        # Solo símbolos
        if re.fullmatch(r"[!?.,:;(){}\[\]\-_=+*/\\|<>~`@#$%^&]+", text):
            return None

        # Muchos caracteres repetidos
        if re.search(r"(.)\1{" + str(self.max_repeated_chars) + ",}", text):
            return None

        return message