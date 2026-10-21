from tts.models import ProviderInfo


class ProviderFactory:

    _providers = {}

    @classmethod
    def register(
        cls,
        name,
        provider,
        version="1.0.0",
        author="Unknown",
        description="",
        local=True,
        cloud=False,
        gpu=False,
        languages=None,
        priority=0,
        capabilities=None
    ):
        """
        Registrar un proveedor de TTS.
        """

        cls._providers[name] = ProviderInfo(
            name=name,
            provider=provider,
            version=version,
            author=author,
            description=description,
            local=local,
            cloud=cloud,
            gpu=gpu,
            languages=languages,
            priority=priority,
            capabilities=capabilities
        )

    @classmethod
    def create(cls, name, *args, **kwargs):
        """
        Crear una instancia del proveedor.
        """

        info = cls._providers.get(name)

        if info is None:
            raise ValueError(
                f"Proveedor '{name}' no registrado."
            )

        return info.provider(*args, **kwargs)

    @classmethod
    def exists(cls, name):
        """
        Comprobar si un proveedor existe.
        """
        return name in cls._providers

    @classmethod
    def unregister(cls, name):
        """
        Eliminar un proveedor.
        """
        cls._providers.pop(name, None)

    @classmethod
    def names(cls):
        """
        Obtener todos los nombres registrados.
        """
        return sorted(cls._providers.keys())

    @classmethod
    def info(cls, name):
        """
        Obtener la información completa de un proveedor.
        """
        return cls._providers.get(name)

    @classmethod
    def providers(cls):
        """
        Obtener todos los proveedores registrados.
        """
        return list(cls._providers.values())

    @classmethod
    def find_by_capability(cls, capability):
        """
        Buscar proveedores que soporten una capacidad.
        """

        result = []

        for provider in cls.providers():

            if capability in provider.capabilities:
                result.append(provider)

        return result

    @classmethod
    def find_by_language(cls, language):
        """
        Buscar proveedores compatibles con un idioma.
        """

        result = []

        for provider in cls.providers():

            if "*" in provider.languages or language in provider.languages:
                result.append(provider)

        return result

    @classmethod
    def best_priority(cls):
        """
        Devuelve los proveedores ordenados por prioridad.
        """

        return sorted(
            cls.providers(),
            key=lambda p: p.priority,
            reverse=True
        )
