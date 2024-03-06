import json
from typing import List, Union, Dict

import aiofiles

from .models import User
from ...config import UPLOADS_DIR


class SocietyStorage:
    """
    A class to manage society-related data storage.

    :param filename: The path to the JSON file for society data storage.
    """

    def __init__(
            self,
            filename: str = f"{UPLOADS_DIR}/json/society-top.json",
    ) -> None:
        """
        Initializes the SocietyStorage instance.

        :param filename: The path to the JSON file for society data storage.
        """
        self.filename = filename

    async def _save(self, data: Union[List, Dict]) -> None:
        """
        Saves data to the specified JSON file asynchronously.

        :param data: The data to be saved.
        """
        async with aiofiles.open(self.filename, "w") as file:
            await file.write(json.dumps(data))

    async def _load(self) -> Dict:
        """
        Loads data from the specified JSON file asynchronously.

        :return: The loaded data.
        """
        async with aiofiles.open(self.filename, "r") as file:
            return json.loads(await file.read())

    async def save_users(self, users: List[User]) -> None:
        """
        Saves a list of User models to the society's top JSON file.

        :param users: The list of User models to be saved.
        """
        data = [user.model_dump() for user in users]
        await self._save(data)

    async def get_users(self) -> List[User]:
        """
        Retrieves a list of User models from the society's top JSON file.

        :return: The list of User models.
        """
        data = await self._load()
        return [User(**user) for user in data]
