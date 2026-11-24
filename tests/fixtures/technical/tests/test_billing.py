from hashlib import sha256
from pathlib import Path
import sqlite3
import unittest

from billing.cache_keys import cache_key
from billing.reminders import next_pending_id, send_reminder


class BillingTests(unittest.TestCase):
    def test_existing_cache_key_format(self):
        self.assertEqual(cache_key("Ö-42"), "account:" + sha256("Ö-42".encode("utf-8")).hexdigest())

    def test_stops_after_success(self):
        outcomes = iter([False, True, False])
        send_reminder(lambda: next(outcomes))
        self.assertIs(next(outcomes), False)

    def test_fails_after_three_attempts(self):
        outcomes = iter([False, False, False, True])
        with self.assertRaisesRegex(RuntimeError, "^Reminder delivery failed$"):
            send_reminder(lambda: next(outcomes))
        self.assertIs(next(outcomes), True)

    def test_preserves_pending_order(self):
        self.assertEqual(next_pending_id([9, 2]), 9)
        self.assertIsNone(next_pending_id([]))

    def test_billing_exception(self):
        root = Path(__file__).resolve().parents[1]
        with sqlite3.connect(":memory:") as connection:
            for migration in sorted((root / "migrations").glob("*.sql")):
                connection.executescript(migration.read_text(encoding="utf-8"))
            connection.executemany("INSERT INTO customers VALUES (?, ?, ?)", [
                (1, True, None),
                (2, False, "2026-11-01"),
                (3, False, "2026-10-31"),
                (4, False, "2026-12-01"),
                (5, False, "2026-11-30"),
            ])
            query = (root / "sql/customer_billing.sql").read_text(encoding="utf-8")
            rows = connection.execute(query, {
                "billing_month_start": "2026-11-01",
                "next_billing_month_start": "2026-12-01",
            })
            self.assertEqual(sorted(rows), [(1, 1), (2, 0), (5, 0)])
