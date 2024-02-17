from typing import Union

from pydantic import BaseModel, field_validator, Field


class User(BaseModel):
    """
    Model representing a TON Society user.

    Attributes:
        id (int): User ID.
        name (str): Name.
        username (str): User username.
        friendly_address (str): User-friendly address.
        telegram_url (Optional[str]): Telegram URL.
        github_url (Optional[str]): GitHub URL.
        awards_count (int): Count of awards.
        society_url (Optional[str]): Society URL.
    """
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
        """ Validates the society URL. """
        return f"https://society.ton.org/profile/{value}"
