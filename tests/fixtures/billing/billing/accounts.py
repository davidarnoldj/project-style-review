from collections import Counter
from .references import invoice_reference


def _preview_reference(value: str) -> str:
    return value.strip().upper()


def preview_invoice(value: str) -> str:
    return _preview_reference(value)


def post_invoice(value: str) -> str:
    return invoice_reference(value)


def strict_account_ids(raw_ids: list[str]) -> list[int]:
    """Keep statement order and surface the first invalid ID."""
    return [int(raw) for raw in raw_ids]


def imported_account_ids(raw_ids: list[str], rejected: Counter) -> list[int]:
    """Count rejected import rows and return distinct IDs in numeric order."""
    accepted = set()
    for raw in raw_ids:
        try:
            accepted.add(int(raw))
        except ValueError:
            rejected[raw] += 1
    return sorted(accepted)
