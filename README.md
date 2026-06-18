# LifePlanner

LifePlanner is a self-hostable personal scheduling app with an automatic weekly planning engine.

## MVP Included

- FastAPI backend with JWT auth and bcrypt hashing
- Bootstrap admin account from env vars
- SQLite default storage with SQLAlchemy + Alembic migrations
- Core models: users, categories, events, settings, schedule runs
- Scheduler modes:
  - `full_auto`
  - `respect_locks`
- Drag/resize/update calendar autosave APIs
- React + Vite + Tailwind frontend
- Dashboard + Calendar (week-first) UI
- Quick category/event management
- Schedule preview/apply workflow
- Manual JSON backup export/import
- Dockerfiles + Docker Compose + Nginx reverse proxy config
- Seed script + backend tests

## Architecture

- `frontend/`: React UI
- `backend/`: FastAPI API + scheduler + persistence
- `nginx/`: reverse proxy config
- `scripts/`: first-time setup scripts
- `docs/`: deployment guides

## API Surface (MVP)

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET/POST/PATCH/DELETE /api/v1/categories`
- `GET/POST/PATCH/DELETE /api/v1/events`
- `POST /api/v1/events/{id}/duplicate`
- `POST /api/v1/scheduler/generate`
- `POST /api/v1/scheduler/apply`
- `GET/PATCH /api/v1/settings`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/backup/export`
- `POST /api/v1/backup/import`

## Quick Start (Local Windows)

1. Copy env:
   - `Copy-Item .env.example .env`
2. Run setup:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`
3. Start backend:
   - `cd backend`
   - `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. Start frontend:
   - `cd frontend`
   - `npm run dev`
5. Open:
   - [http://localhost:5173](http://localhost:5173)

Default bootstrap login comes from env:
- `ADMIN_EMAIL` (default `admin@local.dev`)
- `ADMIN_PASSWORD` (default `admin1234`)

## Seed Sample Data

From repository root:

- `cd backend`
- `.\.venv\Scripts\python.exe scripts/seed_sample_data.py`

Demo account created by seed script:
- `demo@lifeplanner.local`
- `demo1234`

## Run Tests

- `cd backend`
- `.\.venv\Scripts\python.exe -m pytest -q`

## Docker Compose

Primary target command:

- `docker compose up -d --build`

Then open:
- [http://localhost](http://localhost)

Note: Docker CLI was not available in this execution environment, so compose runtime was not smoke-tested here.

## Raspberry Pi Notes

- Keep `.env` values identical across devices except host-specific values (secrets, ports, timezone).
- SQLite persists in Docker volume `lifeplanner_data`.
- Move to Postgres later by changing only `DATABASE_URL` and adding a database service.

See detailed deployment docs:
- [Windows Guide](./docs/DEPLOYMENT_WINDOWS.md)
- [Raspberry Pi Guide](./docs/DEPLOYMENT_RPI.md)

## Known MVP Gaps

- Full Tasks/Goals/Analytics/Templates dedicated pages are placeholders.
- Scheduler is heuristic v1 (deterministic scoring + greedy placement), not global optimization.
- ICS/CSV/PDF import/export are not included yet.
- Frontend tests are not yet included; backend tests are included.
