# Progressively Enhanced Issue Tracker

A server-rendered issue tracker built with **Django** and progressively enhanced with **HTMX**. The application is fully functional with JavaScript disabled — every action works through standard HTML form posts with full-page reloads. When HTMX is active, the same endpoints return small HTML fragments that are swapped into the DOM without a reload.

## Architecture

The core design principle is a single set of Django views that serve **two response modes** based on the `HX-Request` HTTP header:

| Request mode | Header | Response |
|---|---|---|
| Standard (no JS) | none | Full HTML page or 302 redirect |
| Enhanced (HTMX) | `HX-Request: true` | Small HTML fragment (partial) |

```
Browser ── POST /issues/42/update-status/
              │
              ├─ no HX-Request  ──▶ 302 → /projects/1/ (full reload)
              └─ HX-Request     ──▶ 200 → <div class="issue-card">… (DOM swap)
```

Full pages extend `base.html`; fragments live in `tracker/templates/tracker/partials/` (`_issue_card.html`, `_comment.html`, `_issue_form.html`, `_comment_form.html`) and are reused by both the full pages (via `{% include %}`) and the partial responses.

## Models

- **Project** — `name`, `description`
- **Issue** — `title`, `description`, `status` (`todo` / `in_progress` / `done`), `project` (FK), `created_at`, `updated_at`
- **Comment** — `content`, `issue` (FK), `created_at`

## Getting Started (Docker)

Requirements: Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build -d
```

A single `docker compose up` starts both services:

- `db` — PostgreSQL 16 (healthchecked with `pg_isready`)
- `web` — Django + Gunicorn (healthchecked against `/healthz/`)

The `entrypoint.sh` script waits for the database, runs migrations, seeds sample data (idempotent — only seeds when empty), collects static files, and starts Gunicorn.

Then open http://localhost:8000

### Useful commands

```bash
docker compose ps          # verify both services are healthy
docker compose logs -f web # follow application logs
docker compose down        # stop (add -v to remove the database volume)
```

## Configuration (environment variables)

All variables are documented in [.env.example](.env.example):

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Django debug flag (`True`/`False`) |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `DATABASE_URL` | Full PostgreSQL connection URL |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | PostgreSQL credentials |
| `POSTGRES_HOST` / `POSTGRES_PORT` | PostgreSQL host/port |

## Running tests

The test suite in `tracker/tests/` validates **both request modes**:

- **Standard tests** — full pages (200 with `<html>`) and redirects (302) for project boards, issue creation, status updates, and comments.
- **Enhanced tests** — requests sent with `HTTP_HX_REQUEST='true'` assert a 200 response containing only the HTML fragment (no `<html>`/`<body>`), and verify database state.

```bash
docker compose exec web python manage.py test
```

Or locally (uses SQLite for speed):

```bash
set DATABASE_URL=sqlite:///db.sqlite3 && python manage.py test tracker
```

## Endpoints

| Method | URL | Purpose | Standard | HTMX |
|---|---|---|---|---|
| GET | `/` | Project list | Full page | — |
| GET | `/projects/{id}/` | Issue board grouped by status | Full page | — |
| GET | `/issues/{id}/` | Issue detail + comments | Full page | — |
| POST | `/projects/{id}/issues/create/` | Create issue | 302 | card partial |
| POST | `/issues/{id}/update-status/` | Update status | 302 | card partial |
| POST | `/issues/{id}/comments/add/` | Add comment | 302 | comment partial |
| GET | `/healthz/` | Docker healthcheck | JSON | — |
