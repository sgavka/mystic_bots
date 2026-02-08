# TASK_001 — Project skeleton

## Commit ID

*(pending)*

## Summary

Set up the base project infrastructure: Docker (Dockerfile, docker-compose), Django project, Aiogram integration, Poetry for dependencies, Makefile for commands, Redis, PostgreSQL, Celery configuration.

## Checkboxes

- [x] Create `pyproject.toml` with all dependencies (Django, Aiogram, Pydantic, Celery, Redis, dependency-injector, etc.)
- [x] Create `Dockerfile` and `docker-compose.yml` (bot, postgres, redis, celery-worker, celery-beat)
- [x] Create `docker-compose-prod.yml`
- [x] Create `docker/entrypoint.sh`
- [x] Create `Makefile` with all standard commands
- [x] Create `config/settings.py` (Django settings with env vars)
- [x] Create `config/celery.py` (Celery app)
- [x] Create `config/urls.py`, `config/wsgi.py`, `config/asgi.py`
- [x] Create `manage.py`
- [x] Create `.env.example`
- [x] Verify `make build` works (Docker image built successfully)

## Investigation

Based on casino_bots reference project:

- **pyproject.toml**: Poetry-based, Python 3.12+. Add Django 5.2, Aiogram 3.x, Pydantic 2.x, dependency-injector, Redis, psycopg2-binary, Celery, aiohttp, aiofiles. Dev: pytest, pytest-django, pytest-asyncio, aiogram-test-framework, ruff.
- **Dockerfile**: Multi-stage from postgres:17 (for pg tools) + python:3.12-slim. Poetry install inside container.
- **docker-compose.yml**: Services: db (postgres:17), redis (redis:7-alpine), bot, celery-worker, celery-beat. Volumes for code, data.
- **docker-compose-prod.yml**: Similar but with PYTHONOPTIMIZE=2, named services.
- **Makefile**: Copy from casino_bots, adapt container names. Add celery-worker and celery-beat targets.
- **config/settings.py**: Env-based config. BOTS_CONFIG dict built from BotSlug enum. Redis config. Celery config. Logging.
- **config/celery.py**: Standard Celery app with Redis broker, autodiscover_tasks.
- **manage.py**: Standard Django manage.py.
- **.env.example**: DB, Redis, bot token, Celery broker URL, admin IDs.
