"""Worldstate API entrypoint.

Sprint 0: FastAPI skeleton with a health endpoint. The agent loop, memory
writer/retriever and consolidation worker are added in later sprints
(see PROJECT_SPEC.md at the repository root for the plan).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hook.

    Sprint 0 opens no external connections. Later sprints will initialise the
    Postgres pool, Neo4j driver and Redis client here, and close them on
    shutdown.
    """
    yield


def create_app() -> FastAPI:
    """Application factory (kept separate so tests can build fresh instances)."""
    settings = get_settings()
    app = FastAPI(
        title="Worldstate API",
        description="Long-horizon agent with persistent world-model memory.",
        version=settings.service_version,
        lifespan=lifespan,
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        """Liveness probe used by Docker Compose healthchecks and CI."""
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version,
        }

    return app


app = create_app()
