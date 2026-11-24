# Billing Desk operations

## Reuse the existing cache

Keep existing cache entries across upgrades. Earlier versions stored keys with the `account:` prefix followed by the SHA-256 digest of the UTF-8 account ID. Changing either part makes the entries unreachable before their scheduled expiry.
