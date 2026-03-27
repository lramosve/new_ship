# Shipyard

Shipyard is a containerized FastAPI + React workspace for authenticated project, document, issue, plan, and user management.

## Live Demo

The application is deployed on Railway:

- **Frontend:** https://frontend-production-20c1.up.railway.app
- **Backend API:** https://backend-production-d97a.up.railway.app

**Demo account:**
- Email: `dev@ship.dev`
- Password: `admin123`

## Docker quickstart

Run the full stack from the repository root:

```bash
docker compose up --build
```

Endpoints:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Backend health: http://localhost:8000/health
- Frontend-to-backend proxy health: http://localhost:8080/api/health

## What the Docker stack does

- Builds the FastAPI backend from `Dockerfile.backend`
- Builds the Vite/React frontend and serves it with nginx
- Proxies frontend API calls through `/api`
- Persists backend SQLite data in the `shipyard_data` Docker volume
- Runs Alembic migrations automatically every time the backend container starts

## Runtime defaults

The Docker stack uses these local-development defaults:
- `DATABASE_URL=sqlite:///./data/ship_db.db`
- `SECRET_KEY=shipyard-docker-secret`

The SQLite database lives inside the named Docker volume, so data survives container recreation.

## Common Docker commands

Start in the background:

```bash
docker compose up --build -d
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove the persisted SQLite volume:

```bash
docker compose down -v
```

Rebuild only the backend image:

```bash
docker compose build backend
```

View backend logs:

```bash
docker compose logs backend
```

View frontend logs:

```bash
docker compose logs frontend
```

## Authentication

The app exposes `POST /auth/login` for JWT login. After signing in through the frontend, authenticated CRUD operations are available across all resource tabs.

## Additional Docker notes

A shorter Docker-specific reference is also available in `README.docker.md`.
