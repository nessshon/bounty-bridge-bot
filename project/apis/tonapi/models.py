from typing import Union

from pydantic import BaseModel, field_validator, Field


class NftItem(BaseModel):
    """
    Model representing a NFT Item.

    Attributes:
        index (int): The index of the NFT item.
        address (str): The address of the NFT item.
        owner_address (str): The address of the owner of the NFT item.
    """
    index: int
    address: str
    owner_address: Union[str, dict] = Field(alias="owner")

    @field_validator("owner_address", mode="before", check_fields=False)
    def validate_owner_address(cls, value):  # noqa
        """Validates the owner."""
        if isinstance(value, dict):
            return value.get("address")
        return None
