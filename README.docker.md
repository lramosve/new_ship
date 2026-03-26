# Docker runtime

Run the authenticated app stack with one command:

```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

Notes:
- The frontend talks to the backend through `/api` via nginx proxying.
- The backend persists SQLite data in the `shipyard_data` Docker volume.
- The backend uses `SECRET_KEY=shipyard-docker-secret` by default in compose; replace it for non-local environments.
