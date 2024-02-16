from typing import Union

from pydantic import BaseModel, field_validator, Field


class User(BaseModel):
    id: int
    name: str
    username: str
    friendly_address: str
    telegram_url: Union[str, None]
    github_url: Union[str, None]
    awards_count: int
    society_url: Union[str, None] = Field(alias="username")

    @field_validator("society_url", mode="before")
    def validate_society_url(cls, value):  # noqa
        return f"https://society.ton.org/profile/{value}"
