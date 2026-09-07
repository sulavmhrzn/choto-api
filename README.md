# Choto

An API-first URL shortener with Stripe-backed subscription billing, signed outbound webhooks, and a self-managed production deployment.

**Live:** https://choto-api.sulavm.com.np
**API docs:** https://choto-api.sulavm.com.np/api/docs/

There is no web UI. Everything runs through the REST API described in the docs above.

---

## What it does

- **Short links** — create, update, and redirect through custom or generated short codes, with active/expiry state and idempotent creation via an `Idempotency-Key` header.
- **Auth** — JWT login, Google OAuth (django-allauth), and hashed API keys shown once at creation and never re-exposed.
- **Click analytics** — every redirect is recorded asynchronously (Celery) and exposed per-link: totals, unique visitors, and clicks over time.
- **Outbound webhooks** — subscribe to `short_link.created/updated/deleted/clicked` events. Deliveries are HMAC-SHA256 signed, retried on failure (network errors, `408`/`429`/`5xx`) with backoff, and their full attempt history is queryable through the API.
- **Subscription billing** — Stripe Checkout for upgrades, with all entitlement state (plan, status, period dates) driven entirely by verified Stripe webhooks, not client input. Covers activation, renewal, payment failure (grace period via a `past_due` status), and cancellation.
- **Plan enforcement** — short link and webhook endpoint creation are gated by the caller's plan under row-level locks, so concurrent requests can't race past a quota.

## Architecture

Each Django app (`accounts`, `links`, `analytics`, `webhooks`, `billing`, `core`) follows the same internal shape:

- `selectors.py` — read-only queries. Return `None` for "not found," never raise.
- `services.py` — writes and business logic, including anything orchestrating multiple steps atomically.
- `views.py` — thin `APIView`s; no business logic lives here.
- Stripe-specific code is isolated in `apps/billing/providers/stripe.py`, kept out of the domain services entirely.

Side effects that shouldn't fire before a transaction commits (webhook dispatch, cache invalidation) are registered with `transaction.on_commit(...)`.

## Stack

Django · Django REST Framework · PostgreSQL · Redis · Celery (worker + beat) · Docker · Stripe · drf-spectacular · Prometheus/Grafana

## Deployment

Runs on a single DigitalOcean droplet:

- **CI/CD** — GitHub Actions: tests run against real Postgres/Redis services → a multi-stage production image is built and pushed to GHCR, tagged `latest` and by commit SHA → the server pulls and redeploys automatically over SSH, using a forced-command deploy key scoped to exactly one action (`docker compose pull && up -d`), with no interactive shell access.
- **Reverse proxy** — Caddy, terminating TLS with automatic Let's Encrypt certificates. The app container is bound to `127.0.0.1` only and is never reachable except through Caddy.
- **Process model** — `api` (Gunicorn), `celery_worker`, `celery_beat`, and a one-shot `migrate` service all run from the same production image; `db` and `redis` are separate containers with health checks gating startup order.
- **Hardening** — non-root operator account, root SSH login disabled, `ufw` (22/80/443 only), `fail2ban` on SSH, DigitalOcean uptime monitoring on the live HTTP endpoint.
- **Backups** — nightly `pg_dump`, compressed, with 7-day local rotation via cron.

`docker-compose.prod.yml` pulls prebuilt images (`image:`); the server never builds anything. Local development (`docker-compose.yml`) uses `build:` with bind mounts and Django's dev server instead.

## Running locally

```bash
git clone https://github.com/sulavmhrzn/choto-dj-backend.git
cd choto-dj-backend
cp .env.example .env   # fill in Stripe test keys, Google OAuth client, etc.
docker compose up -d
docker compose exec api python manage.py migrate
```

The API is then available at `http://localhost:8000/`, with interactive docs at `/api/docs/`.

Run the test suite with:

```bash
docker compose exec api pytest
```