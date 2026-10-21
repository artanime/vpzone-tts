class SubscriptionService:

    def __init__(self, rest):
        self.rest = rest

    def recent(self, slug):
        """
        Obtiene las suscripciones recientes.
        """
        return self.rest.get(f"/channels/{slug}/subscriptions/recent")