# Makefile for Mystic Bots
# Simplified commands for common development tasks

# Load .env file if it exists
ifneq (,$(wildcard .env))
    include .env
endif

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

# Detect environment from ENV variable or default to dev
ifeq ($(ENV),prod)
	DOCKER_FILE_PART = -f docker-compose-prod.yml
	RUN_CONTAINER = bot_horoscope
else
	DOCKER_FILE_PART = -f docker-compose.yml
	RUN_CONTAINER = bot
endif

# Prevent make from treating arguments as targets
%:
	@:

# =============================================================================
# Docker Management
# =============================================================================

.PHONY: build
build:
	docker compose $(DOCKER_FILE_PART) build $(RUN_ARGS)

.PHONY: start
start:
	docker compose $(DOCKER_FILE_PART) up $(RUN_ARGS) -d

.PHONY: stop
stop:
	docker compose $(DOCKER_FILE_PART) stop $(RUN_ARGS)

.PHONY: restart
restart: stop start

.PHONY: kill
kill:
	docker compose $(DOCKER_FILE_PART) kill $(RUN_ARGS)

.PHONY: ps
ps:
	docker compose $(DOCKER_FILE_PART) ps -a

.PHONY: logs
logs:
	docker compose $(DOCKER_FILE_PART) logs -f $(RUN_ARGS)

.PHONY: logs-all
logs-all:
	docker compose $(DOCKER_FILE_PART) logs -f

.PHONY: recreate
recreate:
	docker compose $(DOCKER_FILE_PART) up -d --force-recreate $(RUN_ARGS)

.PHONY: down
down:
	docker compose $(DOCKER_FILE_PART) down

.PHONY: fresh
fresh: stop
	docker compose $(DOCKER_FILE_PART) down -v
	docker compose $(DOCKER_FILE_PART) up -d --build

# =============================================================================
# Database & Migrations
# =============================================================================

.PHONY: migrate
migrate:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py migrate

.PHONY: makemigrations
makemigrations:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py makemigrations $(RUN_ARGS)

.PHONY: migration-show
migration-show:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py showmigrations

.PHONY: migration-downgrade
migration-downgrade:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py migrate $(RUN_ARGS)

.PHONY: manage
manage:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py $(RUN_ARGS)

# =============================================================================
# Shell Access
# =============================================================================

.PHONY: shell
shell:
	docker compose $(DOCKER_FILE_PART) exec $(RUN_CONTAINER) bash

.PHONY: shell-db
shell-db:
	docker compose $(DOCKER_FILE_PART) exec db psql -U postgres

.PHONY: psql
psql:
	docker compose $(DOCKER_FILE_PART) exec db psql -U postgres

.PHONY: python
python:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python $(RUN_ARGS)

# =============================================================================
# Development
# =============================================================================

.PHONY: install
install: build migrate start

.PHONY: rebuild
rebuild: stop build start

.PHONY: uv-install
uv-install:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) uv sync

.PHONY: uv-add
uv-add:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) uv add $(RUN_ARGS)

.PHONY: uv-update
uv-update:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) uv lock --upgrade

.PHONY: uv-lock
uv-lock:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) uv lock

# =============================================================================
# Celery
# =============================================================================

.PHONY: celery-worker
celery-worker:
	docker compose $(DOCKER_FILE_PART) up -d celery-worker

.PHONY: celery-beat
celery-beat:
	docker compose $(DOCKER_FILE_PART) up -d celery-beat

.PHONY: celery-logs
celery-logs:
	docker compose $(DOCKER_FILE_PART) logs -f celery-worker celery-beat

.PHONY: celery-restart
celery-restart:
	docker compose $(DOCKER_FILE_PART) restart celery-worker celery-beat

# =============================================================================
# Testing
# =============================================================================

.PHONY: test
test:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) pytest $(RUN_ARGS)

.PHONY: test-coverage
test-coverage:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) pytest --cov=. --cov-report=html $(RUN_ARGS)

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: lint
lint:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) ruff check .

.PHONY: format
format:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) ruff format .

# =============================================================================
# I18n
# =============================================================================

.PHONY: i18n-extract
i18n-extract:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py makemessages -l uk -d django
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py makemessages -l en -d django
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py makemessages -l ru -d django

.PHONY: i18n-compile
i18n-compile:
	docker compose $(DOCKER_FILE_PART) run --rm $(RUN_CONTAINER) python manage.py compilemessages

# =============================================================================
# Production Deployment
# =============================================================================

.PHONY: deploy
deploy:
	@echo "Building production containers..."
	docker compose -f docker-compose-prod.yml build
	@echo "Starting services..."
	docker compose -f docker-compose-prod.yml up -d
	@echo "Deployment complete!"

.PHONY: prod-logs
prod-logs:
	docker compose -f docker-compose-prod.yml logs -f $(RUN_ARGS)

.PHONY: prod-ps
prod-ps:
	docker compose -f docker-compose-prod.yml ps -a

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Docker Management:"
	@echo "  make build          - Build Docker containers"
	@echo "  make start          - Start containers in background"
	@echo "  make stop           - Stop containers"
	@echo "  make restart        - Restart containers"
	@echo "  make logs           - View container logs"
	@echo "  make logs-all       - View all service logs"
	@echo "  make ps             - List containers"
	@echo "  make recreate       - Force recreate containers"
	@echo "  make down           - Stop and remove containers"
	@echo "  make fresh          - Fresh start (removes volumes)"
	@echo ""
	@echo "Database & Migrations:"
	@echo "  make migrate                    - Run pending migrations"
	@echo "  make makemigrations             - Create new migrations"
	@echo "  make migration-show             - Show all migrations"
	@echo "  make migration-downgrade APP    - Migrate to specific app version"
	@echo "  make manage <cmd>               - Run Django manage.py command"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell          - Open bash shell in container"
	@echo "  make shell-db       - Open psql shell in database"
	@echo "  make psql           - Open psql shell in database (alias)"
	@echo "  make python         - Run Python interpreter"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Full setup: build, migrate, start"
	@echo "  make rebuild        - Stop, build and start"
	@echo "  make uv-install     - Install dependencies"
	@echo "  make uv-add         - Add new dependency"
	@echo "  make uv-update      - Update dependencies (upgrade all)"
	@echo "  make uv-lock        - Regenerate lock file"
	@echo ""
	@echo "Celery:"
	@echo "  make celery-worker  - Start Celery worker"
	@echo "  make celery-beat    - Start Celery beat scheduler"
	@echo "  make celery-logs    - View Celery logs"
	@echo "  make celery-restart - Restart Celery services"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Check code with ruff"
	@echo "  make format         - Format code with ruff"
	@echo ""
	@echo "I18n:"
	@echo "  make i18n-extract   - Extract translatable strings"
	@echo "  make i18n-compile   - Compile translation files"
	@echo ""
	@echo "Production:"
	@echo "  make deploy         - Deploy to production"
	@echo "  make prod-logs      - View production logs"
	@echo "  make prod-ps        - List production containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove Python cache files"
	@echo ""
	@echo "Environment:"
	@echo "  ENV=prod make <cmd> - Run command in production mode"
