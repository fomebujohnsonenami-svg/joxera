# Joxera

**Borderless employment marketplace** — blending professional tech contracts with local vocational gigs into one verifiable trust ecosystem.

| Principle | Description |
|-----------|-------------|
| **Inclusive** | Serves corporate developers and local tradespeople equally |
| **Trust-first** | No user interacts with listings until identity-verified |
| **Borderless** | Operates across 195+ countries (ISO 3166-1 alpha-2) |
| **Resume-gap erasure** | Every completed job becomes a signed proof-of-work credential |

## Repository structure

```
joxera/
├── frontend/          # React 18 + Vite + TypeScript + Tailwind CSS
├── backend/           # Django 5.x + DRF + GeoDjango
├── docker/            # docker-compose.yml (PostGIS, Redis, Celery)
└── README.md
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- **Or** for local development without Docker:
  - Node.js 20+
  - Python 3.12+
  - PostgreSQL 16 with [PostGIS](https://postgis.net/)
  - Redis 7+
  - GDAL/GEOS libraries (required for GeoDjango)

## Quick start (Docker)

The fastest way to run the full stack locally:

```bash
cd docker
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |
| Health check | http://localhost:8000/api/health/ |
| Django Admin | http://localhost:8000/admin/ |
| PostgreSQL | `localhost:5432` (user/pass/db: `joxera`) |
| Redis | `localhost:6379` |

### First-time setup inside Docker

Create a superuser after the stack is running:

```bash
docker exec -it joxera-backend python manage.py createsuperuser
```

Stop the stack:

```bash
cd docker
docker compose down
```

Remove volumes (wipes database):

```bash
docker compose down -v
```

## Local development (without Docker)

### 1. Database & Redis

Start PostgreSQL with PostGIS and Redis on your machine, then create the database:

```sql
CREATE USER joxera WITH PASSWORD 'joxera';
CREATE DATABASE joxera OWNER joxera;
\c joxera
CREATE EXTENSION postgis;
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # edit values as needed
python manage.py migrate
python manage.py runserver
```

In a second terminal, start Celery:

```bash
cd backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
celery -A config worker --loglevel=info
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173.

## Environment variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | — | Django secret key |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_DB` | `joxera` | Database name |
| `POSTGRES_USER` | `joxera` | Database user |
| `POSTGRES_PASSWORD` | `joxera` | Database password |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
| `CSRF_TRUSTED_ORIGINS` | — | Required in production (HTTPS origins) |
| `DJANGO_ENV` | `development` | Set to `production` for hardening |
| `THROTTLE_ANON` | `100/hour` | Anonymous API rate limit |
| `THROTTLE_USER` | `1000/hour` | Authenticated API rate limit |
| `ALLOW_KYC_SIMULATION` | `False` | Enable dev KYC bypass (E2E only) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## Tech stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, React Router |
| Backend | Django 5.x, Django REST Framework, GeoDjango |
| Database | PostgreSQL 16 + PostGIS |
| Task queue | Celery + Redis |
| Containerization | Docker Compose |

## Testing

### Backend (pytest-django)

```bash
cd backend
pip install -r requirements-dev.txt
export POSTGRES_HOST=localhost POSTGRES_DB=joxera_test
python manage.py migrate
pytest
```

Coverage includes:
- **Auth gating** — unverified users blocked from mutating listings
- **Escrow atomicity** — wallet deductions, idempotent release, refund guards
- **Webhook signatures** — Stripe/dLocal/Persona HMAC rejection

### Frontend E2E (Playwright)

```bash
# Start backend stack first (docker compose up)
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

Flow: register → KYC simulate → post job → apply → escrow fund → dual sign-off → release → wallet + profile credential.

## Production deployment

```bash
cd docker
cp .env.prod.example .env.prod   # fill in secrets
docker compose -f docker-compose.prod.yml up --build -d
```

| Service | Image | Notes |
|---------|-------|-------|
| `backend` | `backend/Dockerfile.prod` | Gunicorn WSGI, 4 workers |
| `celery` | same image | Async task worker |
| `frontend` | `frontend/Dockerfile.prod` | Vite build → Nginx |
| `db` | PostGIS + pgvector | Persistent volume |

Production security (when `DJANGO_ENV=production`):
- `SECURE_PROXY_SSL_HEADER` for reverse-proxy TLS
- `CSRF_TRUSTED_ORIGINS` + `CORS_ALLOWED_ORIGINS`
- DRF `AnonRateThrottle` / `UserRateThrottle`
- Secure cookies + HSTS

### CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:
1. Ruff lint + pytest (PostGIS service)
2. ESLint + TypeScript build
3. Docker image builds
4. Playwright E2E against live stack

## API overview

All authenticated endpoints require identity verification (to be implemented). Public endpoints:

- `GET /api/health/` — service health check

## License

Proprietary — Joxera. All rights reserved.
