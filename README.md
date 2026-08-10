# Progressively Enhanced Issue Tracker

This is a Django-based Kanban issue tracker that uses **HTMX** for progressive enhancement. 

The core goal of the project was to build a system that works perfectly out of the box with standard HTML forms (with JavaScript completely disabled), but feels like a modern single-page app when JavaScript is enabled by dynamically swapping HTML fragments into the DOM.

---

## How the Architecture Works

Instead of separating the codebase into a backend API and a frontend SPA, the application uses a single set of Django views that serve **two response modes** depending on whether the request was made via HTMX:

* **Standard Request (No JS):** Returns a full HTML page or a `302 redirect`.
* **Enhanced Request (HTMX):** Receives the `HX-Request: true` header and returns only a small HTML fragment (a template partial), which HTMX swaps directly into the page.

All reusable fragments (like issue cards, comment bubbles, and forms) live in `tracker/templates/tracker/partials/`. They are shared: the full-page views render them using Django's `{% include %}` tag, and the HTMX views return them directly.

---

## Getting Started (Docker)

To run the entire setup (Django + PostgreSQL) in Docker:

```bash
# 1. Copy the example env file
cp .env.example .env

# 2. Spin up the containers
docker compose up --build -d
```

This starts two services:
1. `db`: PostgreSQL 16 (configured with a database health check).
2. `web`: Django + Gunicorn (health checked via `/healthz/`).

On start, the container runs database migrations, seeds some sample data (only if the database is empty), collects static files, and starts Gunicorn.

Once running, open **http://localhost:8000** in your browser.

### Handy Docker Commands
```bash
docker compose ps          # Check container status/health
docker compose logs -f web # Follow the web server logs
docker compose down        # Stop the services
```

---

## Local Development (Without Docker)

If you prefer to run it locally without Docker, the application automatically falls back to **SQLite** so you don't need to install or run Postgres.

```bash
# 1. Set up a virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create env file
copy .env.example .env     # On Windows
# cp .env.example .env     # On macOS/Linux

# 4. Migrate and seed database
python manage.py migrate
python manage.py seed_data

# 5. Start the server
python manage.py runserver
```

---

## Running the Test Suite

The test suite validates both standard full-page reloads/redirects and HTMX fragment responses.

**To run tests inside Docker:**
```bash
docker compose exec web python manage.py test
```

**To run tests locally (uses SQLite):**
```bash
python manage.py test tracker
```

**For Windows terminal (with explicit database settings):**
```powershell
$env:DATABASE_URL="sqlite:///db.sqlite3"; python manage.py test tracker
```

---

## Project Structure & Endpoints

### Models
* **Project:** Holds issues (`name`, `description`).
* **Issue:** Tasks with status `todo`, `in_progress`, or `done`. Linked to a project.
* **Comment:** Simple text comments linked to an issue.

### URL Endpoints
* `GET /` — Project list page
* `GET /projects/<id>/` — Kanban board for a project
* `GET /issues/<id>/` — Issue detail and comment view
* `POST /projects/<id>/issues/create/` — Create a new issue (redirects on standard, returns card partial on HTMX)
* `POST /issues/<id>/update-status/` — Update an issue's status (redirects on standard, returns card partial on HTMX)
* `POST /issues/<id>/comments/add/` — Comment on an issue (redirects on standard, returns comment partial on HTMX)
* `GET /healthz/` — Health check endpoint for Docker/Gunicorn

---

## Design Decisions & Trade-offs

### 1. Progressive Enhancement over SPA Architecture
Using a single Django codebase rather than a split Django-REST/React setup saved a massive amount of development overhead. By leveraging HTMX, we get 90% of the SPA user experience with 10% of the complexity. If JS is disabled or fails to load, the site still functions completely.

### 2. Dual-Mode Views (`_is_htmx`)
I wrote a small helper function `_is_htmx(request)` that checks for the `HX-Request` header. This serves as a clean branch point in the views. If true, we render the target partial; if false, we redirect or render the full page. Keeping this logic in function-based views makes the flow very easy to trace.

### 3. Dry Templates using Shared Partials
I placed the partial templates inside a `partials/` folder. This ensures that the code for rendering an issue card or a comment is defined in exactly one place. When Django renders the project board, it loops and includes `_issue_card.html`. When HTMX updates an issue's status, it hits the view and returns that exact same `_issue_card.html` file. 

### 4. Zero-Config Local Development
To make onboarding and local testing painless, the `settings.py` file uses `sqlite:///db.sqlite3` as a default if `DATABASE_URL` is missing. This means developers can run tests or start the server locally in a clean environment without needing to install or manage a Postgres server.

### 5. Whitenoise for Simple Assets
I chose Whitenoise to serve static files. It hooks directly into Django's WSGI application flow, compressing and caching files. This avoids the overhead of setting up and maintaining an Nginx container just to serve simple CSS and HTMX scripts.

### 6. Robust Container Startup
The `entrypoint.sh` script runs a python snippet that retries the database connection for up to 60 seconds before throwing an error. This prevents the web container from crashing if Postgres takes a few seconds longer to start up on a cold run.
