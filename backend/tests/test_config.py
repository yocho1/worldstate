"""Settings layer tests."""

from app.config import Settings


def test_settings_defaults():
    settings = Settings(_env_file=None)  # ignore any local .env for determinism
    assert settings.service_name == "worldstate-api"
    assert settings.postgres_host == "localhost"
    assert settings.redis_url == "redis://localhost:6379/0"


def test_database_url_is_composed_from_parts():
    settings = Settings(
        _env_file=None,
        postgres_user="alice",
        postgres_password="secret",
        postgres_host="db.internal",
        postgres_port=6543,
        postgres_db="worldstate_test",
    )
    assert (
        settings.database_url
        == "postgresql://alice:secret@db.internal:6543/worldstate_test"
    )
