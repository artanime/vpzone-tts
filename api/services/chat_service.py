class ChatService:

    def __init__(self, rest):
        self.rest = rest

    def recent(self, slug):
        """
        Obtiene los últimos mensajes del chat.
        """
        return self.rest.get(f"/channels/{slug}/chat")