from typing import List

from .models import User
from ..client import ClientAPI


class TONSocietyAPI(ClientAPI):
    """
    Asynchronous TON Society API client for fetching issue-related data.
    """

    def __init__(
            self,
            base_url: str = "https://society.ton.org",
    ) -> None:
        """
        Initializes the TON Society object.

        :param base_url: Base URL for TON Society API (default is "https://society.ton.org").
        """
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "  # noqa
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        super().__init__(base_url, headers=self.headers)

    async def get_user(self, username: str) -> User:
        """
        Retrieves a user by username from the TONSocietyAPI.

        :param username: Username of the user.
        """
        method = f"/v1/users/{username}"
        result = await self._get(method)
        return User(**result["data"].get("user"))

    async def get_users(self, start: int = 0, end: int = 100) -> List[User]:
        """
        Retrieves the top contributors from the TONSocietyAPI.

        :param start: Start index for the users list.
        :param end: End index for the users list.
        """
        method = f"/v1/users"
        params = {"_start": start, "_end": end}
        result = await self._get(method, params=params)
        return [User(**user) for user in result["data"].get("users")]

    async def get_users_by_collection(
            self,
            collection_id: int,
            start: int = 0,
            end: int = 100
    ) -> List[User]:
        method = f"/v1/users-by-collections/{collection_id}"
        params = {"_start": start, "_end": end}
        result = await self._get(method, params=params)
        return [User(**user) for user in result["data"].get("users")]

    async def get_all_users_by_collection(
            self,
            collection_id: int,
    ) -> List[User]:
        start, end = 0, 100
        users = []
        while True:
            result = await self.get_users_by_collection(collection_id, start, end)
            if not result:
                break
            users.extend(result)
            start += 100
            end += 100
        return users
