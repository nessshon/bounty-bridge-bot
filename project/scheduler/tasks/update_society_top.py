from ...apis.society import TONSocietyAPI
from ...apis.society.storage import SocietyStorage
from ...apis.tonapi import TONAPI
from ...config import load_config, BOUNTIES_COLLECTION_ADDRESS


async def update_society_top() -> None:
    """Updates the society's contributors top data by fetching it from the TON Society API."""

    # Load configuration
    config = load_config()

    # Initialize TON Society API, Society Storage, and TON API with the provided key
    society_api = TONSocietyAPI()
    society_storage = SocietyStorage()
    tonapi = TONAPI(config.TONAPI_KEY)

    # Fetch all bounty NFT items from the collection address
    bounty_items = await tonapi.get_all_items_by_collection(BOUNTIES_COLLECTION_ADDRESS)
    # Fetch all users from the TON Society API for the specified collection ID
    bounty_users = await society_api.get_all_users_by_collection(44)

    # Update each bounty user with raw and friendly addresses
    for bounty_user in bounty_users:
        user = await society_api.get_user(bounty_user.username)
        bounty_user.raw_address = user.raw_address
        bounty_user.friendly_address = user.friendly_address

    # Calculate awards count for each user based on ownership of bounty items
    for user in bounty_users:
        user.awards_count = len(
            [i for i in bounty_items if i.owner_address == user.raw_address]
        )

    # Sort users based on awards_count in descending order
    society_top = sorted(bounty_users, key=lambda x: x.awards_count, reverse=True)
    if any(society_top):
        # Save the updated society top data to storage
        await society_storage.save_users(society_top)
