from typing import Dict, Any

import aiohttp


class ClientAPI:
    """
    Asynchronous API client for fetching issue-related data.
    """

    def __init__(
            self,
            base_url: str,
            headers: Dict = None,
    ) -> None:
        """
        Initializes the API client object.

        :param base_url: Base URL for the API.
        """
        self.base_url = base_url
        self.headers = headers or {}

    async def _get(
            self,
            method: str,
            params: dict = None,
    ) -> Any:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    self.base_url + method,
                    params=params,
            ) as response:
                return await response.json()
