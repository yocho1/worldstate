# worldstate — Long-Horizon Agent with Persistent World-Model Memory

An agent that stays coherent over 100+ turns by maintaining a structured, queryable
**world-model** — a bi-temporal entity/relationship graph, an explicit task-state
store, and a vector-indexed episodic log — instead of relying on context truncation
or lossy summarization. Benchmarked head-to-head against a naive baseline agent.

> **Read [`PROJECT_SPEC.md`](PROJECT_SPEC.md) first** — it is the canonical
> architecture, sprint plan, and progress log for this repository.

## Architecture

```
Agent Orchestrator (planning + tool-use loop)
        │
        ├── Memory Writer (extraction + update engine, async)
        ├── Memory Retriever (query router + fusion)
        │
World-Model Store:
  ├── Entity/Relationship Graph (Neo4j) — bi-temporal facts
  ├── Task-State Store (Postgres) — explicit task/subtask/blocker tracking
  └── Episodic Log (Postgres + pgvector) — raw turn history, vector-indexed

Consolidation Worker (background job: dedupe, decay stale facts, archive tasks)
```

## Quickstart (Docker)

Prerequisites: Docker Desktop (or Engine + Compose v2).

```bash
cp .env.example .env          # fill in your ANTHROPIC_API_KEY
docker compose up --build     # starts postgres, neo4j, redis, api
```

Once healthy:

- API health: http://localhost:8000/health
- API docs (Swagger UI): http://localhost:8000/docs
- Neo4j browser: http://localhost:7474 (user `neo4j`, password from `.env`)

Stop everything and keep data: `docker compose down`
Stop and wipe data: `docker compose down -v`

## Local development (without Docker for the API)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # Windows (bash: source .venv/bin/activate)
pip install -r backend/requirements-dev.txt

# run the API
cd backend
uvicorn app.main:app --reload

# run tests
pytest -m "not integration"
```

Postgres/Neo4j/Redis still need to run somewhere for integration tests —
use `docker compose up -d postgres neo4j redis`.

## Testing

```bash
cd backend
pytest                      # unit tests (no backing services needed)
pytest -m integration       # integration tests (require the Docker services)
ruff check .                # lint
```

CI (`.github/workflows/ci.yml`) runs ruff, the unit tests, and a Docker Compose
smoke test that boots every service and waits for all healthchecks to pass.

## Project structure

```
backend/
  app/
    main.py        # FastAPI app + health endpoint (Sprint 0)
    config.py      # settings from environment/.env
  tests/           # pytest suite (unit + integration markers)
docker-compose.yml # postgres (pgvector), neo4j, redis, api
.github/workflows/ # CI
```

## Status

Sprint-by-sprint progress lives in the
[Progress Log](PROJECT_SPEC.md#6-progress-log) of `PROJECT_SPEC.md`.
