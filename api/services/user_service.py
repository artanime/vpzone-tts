class UserService:

    def __init__(self, rest):
        self.rest = rest

    def me(self):
        """
        Obtiene información del usuario autenticado.
        """
        return self.rest.get("/me")