from dataclasses import dataclass

from api.models.base_model import BaseModel


@dataclass
class Channel(BaseModel):

    id: int | None = None

    slug: str | None = None

    display_name: str | None = None

    avatar_url: str | None = None

    verified: bool = False

    followers: int = 0