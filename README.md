# AI OS

## Local dev (WSL + Pipenv)

### Prereqs

- WSL2 (Ubuntu recommended)
- Python 3.11
- Docker Desktop with WSL integration enabled
- Pipenv

### Setup

```bash
pipenv install
cp .env.example .env
```

### Run (Docker Compose)

```bash
docker compose up -d --build
```

- API health: `http://localhost/health` (via Caddy)
- Direct API (if you bypass Caddy): `http://localhost:8000/health`

### WhatsApp webhook

- Verify endpoint: `GET /webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...`
- Inbound endpoint: `POST /webhooks/whatsapp` with `X-Hub-Signature-256: sha256=<hex>`

## Notes

- The repo uses `Pipfile` as the dependency source of truth; `requirements.txt` is kept for compatibility.

