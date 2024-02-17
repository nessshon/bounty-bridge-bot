from typing import Dict

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

    async def _get(self, method: str) -> Dict:
        """
        Sends an HTTP GET request to the API.

        :param method: API method.
        :return: JSON response from the API.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.base_url + method) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get {self.base_url}{method}: {response.status}")
                return await response.json()
