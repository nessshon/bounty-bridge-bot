from typing import Union

from pydantic import BaseModel, field_validator, Field


class User(BaseModel):
    """
    Model representing a TON Society user.

    Attributes:
        id (str): User ID.
        name (str): Name.
        username (str): User username.
        awards_count (int): Count of awards.
        society_url (Optional[str]): Society URL.
    """
    id: str
    name: str
    username: str
    awards_count: int
    society_url: Union[str, None] = Field(alias="username")

    @field_validator("society_url", mode="before")
    def validate_society_url(cls, value):  # noqa
        """ Validates the society URL. """
        return f"https://society.ton.org/profile/{value}"


class SBT(BaseModel):
    """
    Model representing a TON Society SBT.

    Attributes:
        id (int): SBT ID.
        sbt_collections_id (int): SBT collection ID.
        content_uri (Optional[str]): SBT Content URI.
        name (Optional[str]): SBT Name.
        image (Optional[str]): Image url.
        sbt_collection_address (str): SBT collection address.
    """
    id: int
    sbt_collections_id: int
    content_uri: Union[str, None]
    name: Union[str, None]
    image: Union[str, None]
    sbt_collection_address: str
