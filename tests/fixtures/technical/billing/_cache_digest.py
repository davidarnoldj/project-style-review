from hashlib import sha256


def digest_account_id(account_id: str) -> str:
    return sha256(account_id.encode("utf-8")).hexdigest()
