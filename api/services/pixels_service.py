class PixelsService:

    def __init__(self, rest):
        self.rest = rest

    def recent(self, slug):
        """
        Obtiene los últimos Pixels.
        """
        return self.rest.get(f"/channels/{slug}/pixels/recent")