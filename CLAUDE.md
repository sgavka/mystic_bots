# Mystic Bots — CLAUDE.md

## Project Concept

Telegram bot platform for generating personalized horoscopes. Users go through a wizard (name → birth date → birth place → living place), receive their first horoscope, and then get daily horoscopes. Free users see a teaser (few lines); subscribers get the full horoscope. Horoscope generation runs via Celery task queue.

## Project Structure

```
mystic_bots/
├── CLAUDE.md                  # This file — development rules & project overview
├── PLAN.md                    # Current plan, task list, next step
├── docs/
│   ├── MAIN.md                # Development process summary
│   └── tasks/                 # Individual task files (TASK_{number}_{status}.md)
├── Makefile                   # Build/dev automation (all commands go through here)
├── docker-compose.yml         # Development environment
├── docker-compose-prod.yml    # Production environment
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── pyproject.toml             # uv dependencies (PEP 621)
├── manage.py                  # Django management entry point
├── config/
│   ├── settings.py            # Django settings
│   ├── celery.py              # Celery app configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                      # Core app (shared across bots)
│   ├── models.py              # User, Payment, Setting models
│   ├── entities.py            # Pydantic entities
│   ├── enums.py               # BotSlug, etc.
│   ├── containers.py          # DI container
│   ├── base_entity.py
│   ├── repositories/
│   └── services/
├── telegram_bot/              # Telegram bot base app
│   ├── bot.py                 # Bot factory, dispatcher setup
│   ├── models.py
│   ├── entities.py
│   ├── states.py              # FSM states
│   ├── handlers/
│   ├── middlewares/
│   │   ├── bot.py             # BotMiddleware
│   │   └── user.py            # UserMiddleware, AppContextMiddleware
│   ├── repositories/
│   ├── services/
│   ├── utils/
│   │   └── context.py         # AppContext for message management
│   └── management/commands/
│       └── start_bot.py
├── horoscope/                 # Horoscope bot app (main feature)
│   ├── models.py              # UserProfile, Horoscope, Subscription
│   ├── entities.py
│   ├── enums.py               # SubscriptionStatus, HoroscopeType
│   ├── config.py
│   ├── callbacks.py           # Callback data structures
│   ├── keyboards.py           # Inline keyboard builders
│   ├── states.py              # FSM states (wizard)
│   ├── tasks/                 # Celery tasks
│   │   ├── generate_horoscope.py
│   │   └── send_daily_horoscope.py
│   ├── handlers/
│   │   ├── wizard.py          # Onboarding wizard
│   │   ├── horoscope.py       # View horoscope
│   │   ├── subscription.py    # Manage subscription
│   │   └── menu.py            # Main menu
│   ├── repositories/
│   ├── services/
│   │   ├── horoscope.py       # Generation logic
│   │   └── subscription.py    # Subscription logic
│   └── tests/
├── locale/                    # i18n translations
│   ├── en/
│   ├── uk/
│   └── ru/
└── data/
    ├── postgres/
    └── redis/
```

## Tech Stack

- **Python** 3.12+
- **Django** 5.2 — ORM, migrations, management commands
- **Aiogram** 3.x — Telegram bot framework (async)
- **Pydantic** 2.x — entities, validation
- **PostgreSQL** 17 — database
- **Redis** 7 — FSM storage, Celery broker, cache
- **Celery** — task queue for horoscope generation
- **dependency-injector** — DI container
- **Docker** + **docker-compose** — containerized dev/prod
- **uv** — dependency management

## Development Rules

### Commands — ALWAYS use Makefile

Never run `python manage.py` or `celery` directly. Always use:

```bash
make build              # Build containers
make start              # Start all services
make stop               # Stop all services
make restart            # Restart
make logs               # View logs
make migrate            # Run migrations
make makemigrations     # Create migrations
make manage <cmd>       # Any manage.py command
make test               # Run tests
make lint               # Linting
make format             # Code formatting
make celery-worker      # Start Celery worker
make celery-beat        # Start Celery beat
```

### Architecture Patterns

1. **DRY (Don't Repeat Yourself)** — no code duplication; extract shared logic into services/utils. Every piece of knowledge must have a single, unambiguous representation.

2. **DDD (Domain-Driven Design)** — organize code by domain (horoscope, core, telegram_bot). Keep domain logic in services, use entities as value objects, repositories as data access boundaries.

3. **Repository Pattern** — all data access through repositories returning Pydantic entities (NEVER return Django models directly)
   - Sync methods: `get_by_id`, `create`, `update`, `filter`, `delete`
   - Async methods: `aget_by_id`, `acreate`, `aupdate`, `afilter`, `adelete`

4. **Entity Pattern** — every Django model has a corresponding Pydantic entity with `model_config = ConfigDict(from_attributes=True)`

5. **Dependency Injection** — use `dependency-injector` framework
   - Inject only in: method/function parameters or class `__init__`
   - NEVER inject as class attributes

6. **Middleware Pattern** — auto-apply to all handlers (NO per-handler decorators)
   - BotMiddleware → UserMiddleware → AppContextMiddleware

7. **Service Layer** — business logic lives in services, never in handlers or repositories

### Coding Rules

- ALL function parameters MUST have type hints
- Functions with 3+ arguments MUST use named parameters at call site
- All handlers MUST be async
- All repository methods that touch DB MUST have async variants
- Use `aiohttp` for HTTP requests, `aiofiles` for file operations
- Configuration via environment variables only (never hardcode secrets)
- Celery tasks handle horoscope generation — keep handlers lightweight

### Multi-Bot Pattern

The project supports multiple bots from a single codebase via `BotSlug` enum:

```python
class BotSlug(str, Enum):
    HOROSCOPE = "horoscope"
```

Each bot is started with: `make manage start_bot --bot horoscope`

Bot-specific settings are loaded from environment variables: `BOT_HOROSCOPE_TOKEN`, etc.

### Testing

- Base test class per app (e.g., `HoroscopeTestCase`)
- Use `aiogram-test-framework` for handler tests
- Run: `make test`

### Git & Commits

- Feature branches from `main`
- One logical change per commit
- Commit message format:
  ```
  type: short description

  - Detailed point 1;
  - Detailed point 2;
  - More details as needed.
  ```
- Types: `feat`, `improvement`, `fix`, `refactor`, `docs`, `test`, `chore`
- **IMPORTANT**: Do NOT add "Generated with Claude Code" or similar attribution
- **IMPORTANT**: Do NOT add "Co-Authored-By" lines
- Keep commit messages clean and focused on changes only

### Background Tasks (Celery)

- All horoscope generation goes through Celery task queue
- Daily horoscope delivery via Celery Beat schedule
- Tasks must be idempotent
- Use Redis as broker

## Bot Flow

### Onboarding Wizard
1. User sends `/start`
2. Bot asks for **name**
3. Bot asks for **full date of birth** (DD.MM.YYYY)
4. Bot asks for **place of birth** (city)
5. Bot asks for **place of living** (city)
6. Bot generates first horoscope (via Celery task)
7. Bot delivers horoscope to user

### Daily Horoscope
- Celery Beat triggers daily generation
- Each user gets a personalized horoscope queued as a Celery task
- **Free users**: see teaser (first few lines) + subscription CTA
- **Subscribers**: see full horoscope

### Subscription
- Subscription unlocks full daily horoscope
- Payment via Telegram Stars or other payment provider
- Subscription status tracked in DB
