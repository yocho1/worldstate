"""Shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """A TestClient running the app's full lifespan (startup + shutdown)."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
