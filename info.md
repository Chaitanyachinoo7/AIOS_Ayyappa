# AI OS Codebase Guide

This repository is a production-oriented scaffold for an **AI Operating System (AI OS)**: a cloud-hosted, event-driven backend that ingests triggers (webhooks or schedules), persists them, then processes them asynchronously via workers. It also includes a tiered file-based **context hub** intended for agent memory and operational knowledge.

## Tech Stack

- **Language**: Python 3.11+
- **API**: FastAPI + Uvicorn
- **Reverse proxy**: Caddy (HTTP reverse proxy)
- **Task queue**: Celery
- **Broker/Backend**: Redis
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Context hub**: filesystem folder `context-hub/` + optional Git sync via GitPython
- **AI agent layer**: Pydantic AI with Anthropic models (default `claude-sonnet-4-6`)
- **Monitoring**: Sentry SDK (optional via env var)
- **Containerization**: Docker Compose + Dockerfile
- **Dependency management**: Pipenv (`Pipfile` is the source of truth)

## Repository Layout

At the root:

- `app/`: Python application code
- `context-hub/`: tiered, file-based knowledge store for agents
- `docker-compose.yml`: service composition (api/worker/beat/redis/postgres/caddy)
- `Dockerfile`: Python container image build
- `Pipfile`: dependencies (Pipenv)
- `.env.example`: environment variable template
- `Caddyfile`: reverse proxy configuration
- `.github/workflows/deploy.yml`: CI/CD placeholder

### `app/` structure (by concern)

#### API layer

- `app/main.py`: FastAPI entrypoint; mounts webhooks under `/webhooks/*`
- `app/webhooks/router.py`: router aggregator
- `app/webhooks/whatsapp.py`: WhatsApp webhook endpoints
- `app/webhooks/base.py`: shared helpers (HMAC verification, safe JSON parsing)

#### Persistence

- `app/database.py`: SQLAlchemy engine + session helper
- `app/models/event.py`: `Event` table (source, status, payload, headers, errors)
- `app/models/result.py`: `Result` table (event_id, kind, output)

#### Async execution

- `app/worker.py`: Celery app initialization
- `app/tasks.py`: Celery tasks and routing from `Event` → handler
- `app/scheduler.py`: Celery Beat schedule definition

#### Workflows (DAG)

- `app/workflows/engine.py`: minimal DAG engine (`Node` + dependency resolution)
- `app/workflows/content/daily_report.py`: example workflow graph

#### Agent layer

- `app/agents/dispatcher.py`: routes WhatsApp events into the agent; attempts to reply back
- `app/agents/lightweight.py`: Pydantic AI agent runner + a sample tool (`save_idea`)
- `app/agents/heavyweight.py`: placeholder (not wired yet)
- `app/agents/soul.md`: identity/instructions prepended to agent behavior

#### Integrations

- `app/integrations/whatsapp_payload.py`: extracts sender + message text from WhatsApp payloads
- `app/integrations/whatsapp_client.py`: sends WhatsApp text replies via Graph API
- `app/integrations/slack_client.py`: placeholder
- `app/integrations/anthropic_client.py`: placeholder

#### Context hub Git helper

- `app/context_hub/repo.py`: optional `pull_latest()` and `commit_and_push()` wrapper (GitPython)

### `context-hub/` structure

This folder implements a tiered context system. Each top-level folder contains:

- `abstract.md`: one-line purpose
- `overview.md`: short description (~10 lines)
- optional additional content files

Folders included:

- `identity/`: mission, values, goals
- `inbox/`: temporary capture area (agents can append ideas)
- `areas/`, `projects/`, `knowledge/`: long-lived working sets
- `archive/`: inactive material

## Architecture (Three Layers)

This scaffold implements the three-layer model:

### Layer 1 — Trigger-based actions (Webhooks)

1. FastAPI receives webhook request.
2. Signature is verified (HMAC SHA-256 for WhatsApp).
3. Event is persisted to PostgreSQL immediately.
4. API enqueues async processing via Celery (`process_event`).
5. API returns quickly (no heavy work inline).

Current implementation: WhatsApp webhook in `app/webhooks/whatsapp.py`.

### Layer 2 — Scheduled workflows (Cron)

Celery Beat triggers recurring tasks which call `run_workflow`. Workflows are executed via a simple DAG engine:

- Each node receives a `dict` input and returns a `dict` output.
- Outputs are merged into the shared data payload.
- Dependencies define the execution order.

Current example: `content.daily_report`.

### Layer 3 — Agent layer (Conversational)

Events that represent user messages can be routed into an AI agent:

- The lightweight agent uses **Pydantic AI** + an **Anthropic model**.
- The agent can call tools (example: `save_idea`) to write into the context hub.
- After completion, the dispatcher attempts to send a reply back to the originating platform.

Current wiring: WhatsApp events route to `run_lightweight_agent`.

## Core Data Flow

### Webhook → Event → Celery → Handler

1. `POST /webhooks/whatsapp`
2. Verify signature (`X-Hub-Signature-256`)
3. Insert `Event(status=pending, source="whatsapp")`
4. `celery.send_task("process_event", args=[event_id])`
5. Worker runs `process_event`:
   - marks `Event.status=processing`
   - routes based on `Event.source`
   - writes a `Result` row
   - updates `Event.status=completed|failed`

### Agent → Context hub

The lightweight agent optionally:

- pulls latest context hub content via Git (if `context-hub/` is a valid repo with a remote)
- writes to the context hub filesystem
- commits and pushes changes (if the repo has a configured remote)

## Configuration

The template is in `.env.example`.

Key variables:

- `DATABASE_URL`: Postgres SQLAlchemy URL (docker-compose default points at `postgres` service)
- `REDIS_URL`: Redis broker/backend
- `ANTHROPIC_API_KEY`: enables the agent to call Claude
- `WHATSAPP_*`: verify token, app secret, phone number id, access token
- `SENTRY_DSN`: enables error reporting
- `CONTEXT_HUB_PATH`: path to context hub folder in the container

## Running (high-level)

- Start services: `docker compose up -d --build`
- Health check:
  - via Caddy: `http://localhost/health`
  - direct: `http://localhost:8000/health`

## Design Notes / Insights

- **Persist-before-process**: webhook handlers always write an `Event` row before enqueueing work. This prevents data loss if a worker crashes.
- **Queue-first**: no webhook does heavy processing inline.
- **Traceability**: every operation centers around an `event_id`.
- **DAG workflows**: nodes are pure-ish functions over a shared `dict`, which keeps the workflow runner simple.
- **Context hub discipline**: the repo layout supports cheap scanning (`abstract.md`), selective loading (`overview.md`), then deeper file reads only when needed.

## Current Limitations / Next Hardening Steps

- Database schema is created via `Base.metadata.create_all(...)` at runtime; for production, move to migrations (Alembic).
- WhatsApp webhook verification is implemented; additional webhook sources are scaffold-ready.
- Heavyweight agent is a placeholder; add subprocess-based execution and explicit cost guardrails.
- CI/CD workflow is a placeholder; implement build/deploy and Slack notifications.

