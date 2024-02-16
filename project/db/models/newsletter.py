from __future__ import annotations

from typing import Union

from sqlalchemy import *
from sqlalchemy_file import ImageField
from sqlalchemy_file.validators import SizeValidator

from . import Base


class NewsletterDB(Base):
    """
    Model representing Newsletter table.
    """
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    image = Column(
        ImageField(
            upload_storage="image",
            thumbnail_size=(50, 50),
            validators=[SizeValidator("10M")],
        )
    )
    content = Column(
        VARCHAR(4096),
        nullable=False,
    )
    buttons = Column(
        JSON,
        nullable=True,
        default=None,
    )
    chat_type = Column(
        VARCHAR(8),
        nullable=False,
        default="all",
    )
    created_at = Column(
        DateTime,
        default=func.now(),
    )

    __tablename__ = "newsletters"
    __admin_icon__ = "fas fa-bullhorn"
    __admin_label__ = "Newsletters"
    __admin_name__ = "Newsletter"
    __admin_identity__ = "newsletter"

    @property
    def image_path(self) -> Union[str, None]:
        """Get the path to the image."""
        return self.image.get("url") if self.image and "url" in self.image else None
