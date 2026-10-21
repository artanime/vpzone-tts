from dataclasses import dataclass

from api.models.base_model import BaseModel


@dataclass
class User(BaseModel):

    id: int | None = None

    username: str | None = None

    display_name: str | None = None

    avatar_url: str | None = None

    verified: bool = False