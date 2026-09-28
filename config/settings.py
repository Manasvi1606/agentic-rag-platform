"""Central configuration, loaded once from environment / .env.

This is glue you don't need to write by hand — import `settings` anywhere:

    from config.settings import settings
    conn = psycopg.connect(settings.postgres_dsn)

Design note: keeping all env access in one typed object (rather than scattered
os.getenv calls) is a small but real production habit — it gives you validation
at startup, a single source of truth, and easy overrides in tests.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres / pgvector
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "enterprise_ai"
    postgres_user: str = "app"
    postgres_password: str = "change_me"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenSearch
    opensearch_url: str = "http://localhost:9200"
    opensearch_index: str = "documents"

    # Models
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # LLM serving
    llm_base_url: str = "http://localhost:8001/v1"
    llm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    llm_api_key: str = "not_needed_for_local_vllm"

    # Tools
    web_search_api_key: str = ""

    # App
    log_level: str = Field(default="INFO")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so the .env is parsed exactly once per process."""
    return Settings()


settings = get_settings()
