from dataclasses import dataclass

from api.models.base_model import BaseModel
from api.models.author import Author


@dataclass
class ChatMessage(BaseModel):

    id: int | None = None

    message: str | None = None

    created_at: str | None = None

    author: Author | None = None

    @classmethod
    def from_json(cls, data):

        if data is None:
            return None

        author = None

        if "author" in data and data["author"]:

            author = Author.from_json(
                data["author"]
            )

        return cls(

            id=data.get("id"),

            message=data.get("message"),

            created_at=data.get("created_at"),

            author=author
        )