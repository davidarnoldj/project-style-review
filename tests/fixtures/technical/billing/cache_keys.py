from ._cache_digest import digest_account_id
from ._cache_prefix import cache_prefix


def cache_key(account_id: str) -> str:
    return cache_prefix() + digest_account_id(account_id)
