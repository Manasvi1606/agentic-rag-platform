-- Runs once on first Postgres boot (mounted by docker-compose).
-- Table creation lives in Alembic migrations under database/migrations/,
-- but the extension has to exist before those run.
CREATE EXTENSION IF NOT EXISTS vector;
