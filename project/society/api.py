from typing import Dict, List

import aiohttp

from .models import User


class TONSocietyAPI:
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

    async def _get(self, method: str) -> Dict:
        """
        Sends an HTTP GET request to the TON Society.

        :param method: TON Society method.
        :return: JSON response from the TON Society.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.base_url + method) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get {method}: {response.status}")
                return await response.json()

    async def get_top(self, limit: int = 15) -> List[User]:
        """
        Retrieves the top contributors from the TONSocietyAPI.

        :param limit: The maximum number of contributors to retrieve. Default is 15.
        """
        method = f"/v1/users?_start=0&_end={limit}"
        result = await self._get(method)
        return [User(**user) for user in result.get("users")]
