# Local database setup

## Prepare the database

From the project root, apply the two migrations in order.

```sh
sqlite3 billing.db < migrations/001_create_customers.sql
sqlite3 billing.db < migrations/002_add_suspensions.sql
```
