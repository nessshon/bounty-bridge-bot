from typing import List

from .models import NftItem
from ..client import ClientAPI


class TONAPI(ClientAPI):

    def __init__(
            self,
            api_key: str,
            base_url: str = "https://tonapi.io",
    ):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        super().__init__(base_url, headers=self.headers)

    async def get_nft_items_by_collection(
            self,
            account_id: str,
            limit: int = 100,
            offset: int = 0,
    ) -> List[NftItem]:
        method = f"/v2/nfts/collections/{account_id}/items"
        params = {"limit": limit, "offset": offset}
        result = await self._get(method, params=params)
        return [NftItem(**item) for item in result.get("nft_items", [])]

    async def get_all_items_by_collection(
            self,
            account_id: str,
    ) -> List[NftItem]:
        limit, offset = 100, 0
        items = []
        while True:
            result = await self.get_nft_items_by_collection(account_id, limit, offset)
            if not result:
                break
            items.extend(result)
            offset += limit
        return items
