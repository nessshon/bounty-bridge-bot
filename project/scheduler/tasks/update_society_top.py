from ...apis.society import TONSocietyAPI
from ...apis.society.storage import SocietyStorage


async def update_society_top() -> None:
    """Updates the society's contributors top data by fetching it from the TON Society API."""
    society_api = TONSocietyAPI()
    society_storage = SocietyStorage()

    society_top = await society_api.get_top()
    await society_storage.save_top(society_top)
