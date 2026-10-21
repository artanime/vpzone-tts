import json


class PluginManifest:

    def __init__(
        self,
        plugin_id,
        name,
        version,
        author,
        description,
        entry,
        plugin_class,
        dependencies=None,
        capabilities=None
    ):

        self.id = plugin_id
        self.name = name
        self.version = version
        self.author = author
        self.description = description

        self.entry = entry
        self.plugin_class = plugin_class

        self.dependencies = dependencies or []
        self.capabilities = capabilities or []

    @classmethod
    def from_dict(cls, data):

        return cls(
            plugin_id=data["id"],
            name=data["name"],
            version=data["version"],
            author=data.get("author", ""),
            description=data.get("description", ""),
            entry=data["entry"],
            plugin_class=data["class"],
            dependencies=data.get("dependencies", []),
            capabilities=data.get("capabilities", [])
        )

    @classmethod
    def from_file(cls, filename):

        with open(filename, "r", encoding="utf8") as f:
            data = json.load(f)

        return cls.from_dict(data)
