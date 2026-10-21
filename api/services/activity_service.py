class ActivityService:

    def __init__(self, rest):
        self.rest = rest

    def recent(self, slug):
        """
        Obtiene la actividad reciente.
        """
        return self.rest.get(f"/channels/{slug}/activity/recent")