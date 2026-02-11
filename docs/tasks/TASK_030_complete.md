**Is task investigated** — yes
**Commit ID** — e22c2de
**Summary** — Refactor Celery tasks and services to use DI via container instead of direct instantiation

**Checkboxes**
- [x] Modify `HoroscopeService.__init__` to accept repos as parameters
- [x] Modify `SubscriptionService.__init__` to accept repo as parameter
- [x] Add service factory functions and providers to `core/containers.py`
- [x] Update Celery tasks to get services/repos from container
- [x] Update handlers that directly instantiate services
- [x] Run tests to verify everything works

**Investigation**

Current state:
- Services (`HoroscopeService`, `SubscriptionService`) pull repos from container in their `__init__`
- Celery tasks either pull repos directly from container OR instantiate services directly
- Handlers also instantiate services directly (e.g. `SubscriptionService()`)

Changes needed:
1. **Services**: Accept repos as constructor parameters instead of pulling from container
2. **Container**: Add factory functions and providers for services that wire repos
3. **Celery tasks**: Get fully-wired services from the container
4. **Handlers**: Get services from container instead of direct instantiation

Files to change:
- `core/containers.py` — add service providers
- `horoscope/services/horoscope.py` — accept repos in `__init__`
- `horoscope/services/subscription.py` — accept repo in `__init__`
- `horoscope/tasks/subscription_reminders.py` — use container for services
- `horoscope/tasks/generate_horoscope.py` — use container for services
- `horoscope/tasks/send_daily_horoscope.py` — use container for services/repos
- `horoscope/handlers/subscription.py` — use container for service

**Questions** — none
