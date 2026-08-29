# Project Prompt for GitHub Copilot

> **Instruction for Copilot (read first):**
> Save this entire file as `PROJECT_SPEC.md` in the root of the repository before doing anything else. At the start of every new session or sprint, re-read `PROJECT_SPEC.md` in full before writing any code, so you stay aligned with the architecture, constraints, and current sprint goal. Do not deviate from this spec without flagging the change explicitly. Update the "Progress Log" section at the bottom of this file after each sprint is completed.

---

## 1. Project Overview

**Name:** Long-Horizon Agent with Persistent World-Model Memory

**Problem:** Most LLM agents degrade after ~20-30 turns because they rely on naive context management (truncation or lossy summarization). This project builds an agent that maintains a structured, queryable **world-model** — separate stores for entities/relationships, task state, and episodic history — instead of relying purely on a growing context window or flat vector memory.

**Differentiator (this is the core contribution, not optional):**
1. **Bi-temporal contradiction handling** — when a new fact conflicts with an old one, the old fact is marked superseded (with timestamps), not deleted or silently overwritten.
2. **Typed query routing** — retrieval picks a strategy (direct graph lookup, temporal filter, vector search, or multi-hop traversal) based on the *type* of question, rather than always doing generic vector search.
3. **Explicit task-state tracking** — task progress lives in a structured state store, not buried in chat history or summaries.
4. **Rigorous benchmarking** — the project must include a head-to-head comparison against a naive baseline agent (context truncation/summarization only) on long multi-session tasks, with measured recall accuracy, contradiction handling correctness, token cost, and latency.

**Definition of done:** A working agent + memory system, deployed locally via Docker Compose, with a benchmark report (numbers + charts) proving it outperforms the naive baseline on long-horizon tasks, and a live graph visualization dashboard for demos.

---

## 2. Architecture

```
Agent Orchestrator (planning + tool-use loop)
        │
        ├── Memory Writer (extraction + update engine, async)
        │
        ├── Memory Retriever (query router + fusion)
        │
World-Model Store:
  ├── Entity/Relationship Graph (Neo4j) — bi-temporal facts
  ├── Task-State Store (Postgres) — explicit task/subtask/blocker tracking
  └── Episodic Log (Postgres + pgvector) — raw turn history, vector-indexed

Consolidation Worker (background job: dedupe, decay stale facts, archive completed tasks)
```

## 3. Tech Stack

- **Language/backend:** Python 3.11+, FastAPI
- **LLM:** Anthropic API — Claude Sonnet-class for agent reasoning, Claude Haiku-class for cheap extraction calls
- **Graph DB:** Neo4j Community Edition (Cypher queries)
- **Relational DB:** Postgres (task state, episodic log metadata)
- **Vector store:** pgvector extension on Postgres (keep infra simple — one database)
- **Structured extraction:** Anthropic tool-use / structured outputs with Pydantic schemas (no regex parsing)
- **Async task queue:** Redis + Celery (or asyncio background tasks if scope needs trimming)
- **Observability:** OpenTelemetry traces + a simple Grafana dashboard (or Langfuse if faster to set up)
- **Frontend/dashboard:** Streamlit or a small Next.js app showing the graph updating live
- **Testing:** pytest, with real integration tests against a Dockerized Neo4j/Postgres (not just mocks)
- **Deployment (local):** Docker Compose (Neo4j, Postgres+pgvector, Redis, FastAPI app, dashboard)
- **CI:** GitHub Actions — run tests on every push
- **Version control:** Git, GitHub — see sprint rules below

---

## 4. Working Rules for Copilot

- Work strictly one sprint at a time, in order. Do not start a new sprint until the previous one is tested and pushed.
- Every sprint must end with: (a) passing tests for that sprint's scope, (b) a commit, (c) a push to GitHub, (d) an update to the Progress Log below.
- Write real tests — unit tests for logic (contradiction resolution, query routing), integration tests against actual Dockerized DBs for storage/retrieval. No sprint is "done" without tests that would fail if the sprint's core feature were broken.
- Keep commits scoped to the sprint's goal — don't bundle unrelated changes.
- Use a feature branch per sprint (`sprint-1-skeleton`, `sprint-2-episodic-memory`, etc.), open a PR, then merge to `main` after tests pass. This gives a clean, reviewable history — useful for the portfolio narrative later.
- If a design decision in this spec turns out to be wrong once you start building, stop and flag it explicitly rather than silently improvising — note it in the Progress Log under "Deviations."

---

## 5. Sprint Breakdown

### Sprint 0 — Repo & environment setup
- Initialize repo, `PROJECT_SPEC.md` committed at root
- Docker Compose skeleton: Postgres (with pgvector), Neo4j, Redis, empty FastAPI app
- GitHub Actions CI skeleton (runs on push, currently just lint + empty test suite)
- `.env.example`, README with setup instructions
- **Test:** `docker compose up` succeeds, all containers healthy, CI pipeline runs green on an empty test.
- **Push:** branch `sprint-0-setup` → PR → merge.

### Sprint 1 — Basic agent loop (no memory yet)
- FastAPI endpoint that takes a user message, calls Claude, returns a response
- Simple in-memory conversation history (this is the "naive baseline" — keep it, you'll need it for benchmarking later)
- Basic tool-use scaffolding (agent can call at least one dummy tool)
- **Test:** unit tests for the request/response cycle; a test that sends 3 sequential messages and confirms basic context is preserved within a single session.
- **Push:** branch `sprint-1-agent-loop` → PR → merge.

### Sprint 2 — Task-state store
- Postgres schema + models for `Task { id, goal, status, subtasks, blockers, depends_on }`
- CRUD API for task state
- Agent can create/update/query task state as a tool call
- **Test:** integration tests against real Postgres — create task, update status, verify blockers query returns correct results.
- **Push:** branch `sprint-2-task-state` → PR → merge.

### Sprint 3 — Episodic log + vector recall
- Every turn logged to Postgres, embedded, stored in pgvector
- Semantic search endpoint: given a query, return top-k relevant past turns
- Agent can call this as a memory-retrieval tool
- **Test:** integration test — log N turns, run a semantic query, verify the relevant turn is retrieved.
- **Push:** branch `sprint-3-episodic-memory` → PR → merge.

### Sprint 4 — Entity/relationship graph + extraction pipeline
- Neo4j schema: typed nodes (Person, Fact, Preference, Constraint, etc.), typed edges with `valid_from`, `valid_until`, `observed_at`, `confidence`, `source_episode_id`
- Memory Writer: async extraction pipeline using Claude structured outputs to pull entities/relations from each turn
- Basic ADD logic (no contradiction handling yet — that's Sprint 5)
- **Test:** integration test — feed a turn with a clear fact, verify the correct node/edge appears in Neo4j.
- **Push:** branch `sprint-4-entity-graph` → PR → merge.

### Sprint 5 — Bi-temporal contradiction handling
- Update engine: when new extracted fact conflicts with existing graph fact, mark old edge `invalidated_at`, add new edge, both remain queryable
- Handle ADD / UPDATE / INVALIDATE / NOOP decision logic
- **Test:** this is the most important test in the whole project — feed two contradicting facts in sequence, verify old fact is marked superseded (not deleted), verify a "what's true now" query returns the new fact, and a "what was true then" query returns the old one.
- **Push:** branch `sprint-5-contradiction-handling` → PR → merge.

### Sprint 6 — Query router + fusion retrieval
- Classifier (LLM or rule-based) that routes incoming questions to: direct graph lookup, temporal filter, vector search, or multi-hop traversal
- Fusion layer: merge results into compact structured context for the agent
- Replace naive context-stuffing in the agent loop with routed retrieval
- **Test:** unit tests per query type (mock each retrieval path), integration test confirming router picks correct strategy for sample queries of each type.
- **Push:** branch `sprint-6-query-router` → PR → merge.

### Sprint 7 — Consolidation worker
- Background job (Celery or scheduled task): dedupe near-identical entities, decay/archive low-confidence stale facts, compress completed tasks into archive nodes
- **Test:** integration test — seed duplicate/stale data, run consolidation, verify graph is cleaned up correctly without losing valid current facts.
- **Push:** branch `sprint-7-consolidation` → PR → merge.

### Sprint 8 — Benchmark harness
- Build/adapt a long-horizon multi-session test suite (5-10 tasks, 50-100+ turns each, spanning simulated session gaps, including fact updates and contradictions)
- Run both the naive baseline (Sprint 1's in-memory approach) and the full memory system through it
- Measure: recall accuracy at turn 20/50/100, contradiction-resolution correctness, token cost per turn, added latency, task completion rate
- Output results as a report (markdown + charts)
- **Test:** the benchmark run itself is the test — must be reproducible via a single script/command.
- **Push:** branch `sprint-8-benchmark` → PR → merge.

### Sprint 9 — Dashboard + demo polish
- Simple frontend (Streamlit or Next.js) showing the graph live as the agent works, plus task-state view
- Record a short demo run for the video
- **Test:** smoke test that dashboard loads and reflects current graph state after a live agent interaction.
- **Push:** branch `sprint-9-dashboard` → PR → merge.

### Sprint 10 — Documentation & README polish
- Full README: problem statement, architecture diagram, setup instructions, benchmark results, demo GIF/video link
- Clean up code comments, add docstrings to core modules
- **Test:** fresh clone + `docker compose up` + setup steps in README work end-to-end with no undocumented steps.
- **Push:** branch `sprint-10-docs` → PR → merge → tag release `v1.0`.

---

## 6. Progress Log

*(Copilot: append an entry here after each sprint, noting what was built, test results, and any deviations from this spec.)*

- Sprint 0: _not started_
- Sprint 1: _not started_
- Sprint 2: _not started_
- Sprint 3: _not started_
- Sprint 4: _not started_
- Sprint 5: _not started_
- Sprint 6: _not started_
- Sprint 7: _not started_
- Sprint 8: _not started_
- Sprint 9: _not started_
- Sprint 10: _not started_

### Deviations from spec
*(log any point where implementation diverged from this document, and why)*
