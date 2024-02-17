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

    async def get_top(self, limit: int = 15) -> List[User]:
        """
        Retrieves the top contributors from the TONSocietyAPI.

        :param limit: The maximum number of contributors to retrieve. Default is 15.
        """
        method = f"/v1/users?_start=0&_end={limit}"
        result = await self._get(method)
        return [User(**user) for user in result.get("users")]
