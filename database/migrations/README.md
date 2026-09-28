# Migrations

Managed with Alembic. The extension (`CREATE EXTENSION vector`) is created by
`database/init/01_extensions.sql` on first Postgres boot; Alembic owns the tables.

First-time setup (do this once you've written the models in `database/models.py`):

```bash
alembic init -t async migrations        # or point alembic.ini at this dir
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

TODO: wire `target_metadata = Base.metadata` (from `database.models`) into
`env.py` so autogenerate sees your tables.
