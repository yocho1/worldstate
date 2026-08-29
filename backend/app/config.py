"""Application settings, loaded from environment variables (and a local .env).

Every backing service that appears in later sprints already has its connection
settings declared here, so sprints 1+ only need to start *using* them.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service
    service_name: str = "worldstate-api"
    service_version: str = "0.1.0"
    log_level: str = "INFO"

    # Postgres (task-state store + episodic log, Sprints 2-3)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "worldstate"
    postgres_password: str = "worldstate"
    postgres_db: str = "worldstate"

    # Neo4j (entity/relationship graph, Sprints 4-5)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "worldstate-dev"

    # Redis (broker for the consolidation worker, Sprint 7)
    redis_url: str = "redis://localhost:6379/0"

    # Anthropic (agent reasoning + extraction, Sprint 1+)
    anthropic_api_key: str = ""

    @property
    def database_url(self) -> str:
        """DSN for Postgres (used from Sprint 2 onwards)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (import this, not Settings, in request paths)."""
    return Settings()
