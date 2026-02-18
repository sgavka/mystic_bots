# TASK_061 - Refactor: remove Celery from prod, replace tasks with async background execution

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Remove Celery dependency entirely. Replace Celery tasks with async background functions running in the bot's asyncio event loop. Replace Celery Beat with a simple asyncio-based scheduler for periodic tasks.

## Checklist
- [x] Create `telegram_bot/scheduler.py` — asyncio-based periodic task scheduler
- [x] Convert all 6 Celery tasks to async functions
- [x] Update `horoscope/tasks/messaging.py` to be pure async (use shared bot instance)
- [x] Update handlers (`horoscope.py`, `wizard.py`) to use `asyncio.create_task()` instead of `.delay()`
- [x] Start scheduler during bot `on_startup`, stop on `on_shutdown`
- [x] Remove Celery services from `docker-compose.yml` and `docker-compose-prod.yml`
- [x] Remove Celery config from `config/settings.py` and delete `config/celery.py`
- [x] Remove `celery[redis]` dependency from `pyproject.toml`
- [x] Remove Celery Makefile targets
- [x] Update tests
- [x] Run all tests, lint, verify passing
- [x] Update documentation (CLAUDE.md, PROJECT_INFO.md, .env.example)

## Investigation

### Current state
- 6 Celery tasks in `horoscope/tasks/`:
  - `generate_horoscope_task` — on-demand (called via `.delay()` from handlers)
  - `generate_daily_for_all_users_task` — periodic (daily)
  - `send_daily_horoscope_notifications_task` — periodic (daily)
  - `send_periodic_teaser_notifications_task` — periodic (daily)
  - `send_expiry_reminders_task` — periodic (daily)
  - `send_expired_notifications_task` — periodic (daily)
- `messaging.py` creates new Bot instances and uses `asyncio.run()` (sync→async bridge for Celery)
- Celery Beat schedule in `config/settings.py` with 5 periodic tasks (24h intervals)
- 2 Docker services: `celery-worker` and `celery-beat`

### New approach
1. **On-demand tasks**: Convert to async functions, call via `asyncio.create_task()`
2. **Periodic tasks**: Simple asyncio scheduler that runs tasks at configured intervals
3. **Messaging**: Pure async functions using the shared bot instance (no more `asyncio.run()`)
4. **Scheduler lifecycle**: Start in `on_startup`, cancel in `on_shutdown`
5. **Bot instance**: Pass to scheduler and messaging via parameter (available from start_bot command)

### Key design decisions
- No new dependencies (APScheduler not needed) — simple `asyncio.sleep()` loop
- Scheduler stores references to running asyncio.Tasks for clean shutdown
- Background tasks use async repo methods (already available)
- Errors in background tasks are logged but don't crash the bot

## Questions
_(no questions)_
