# PLAN

## Next step

**TASK_026 in progress** — Replace custom translations with Django gettext.

## Tasks

- [ ] **TASK_026** (processing) — Refactor: use Django/aiogram i18n for translations instead of dict
- [x] **TASK_027** (complete) — Improvement: add "sent at" / "failed to send at" fields to horoscopes table
- [x] **TASK_028** (complete) — Improvement: daily horoscope task sends only teaser part
- [x] **TASK_029** (complete) — Improvement: horoscope generation changes (translate header, teaser logic, subscribe link)
- [x] **TASK_030** (complete) — Refactor: inject services/repos in Celery tasks via DI
- [x] **TASK_022** (complete) — Refactor: use async repo methods instead of inline sync_to_async wrappers
- [x] **TASK_023** (complete) — Improvement: add error handling to critical user paths
- [x] **TASK_024** (complete) — Refactor: extract shared message-sending utility for Celery tasks
- [x] **TASK_025** (complete) — Refactor: consistent language retrieval across handlers
- [x] **TASK_021** (complete) — Feature: add language selection for users
- [x] **TASK_011** (complete) — Refactor: fix repository pattern violations
- [x] **TASK_012** (complete) — Refactor: extract config, keyboards, callbacks per project structure
- [x] **TASK_013** (complete) — Improvement: error handling and Celery retry logic
- [x] **TASK_014** (complete) — Feature: subscription expiry reminders
- [x] **TASK_015** (complete) — Feature: Django admin interface
- [x] **TASK_016** (complete) — Testing: unit tests for services and repositories
- [x] **TASK_017** (complete) — Feature: LLM-based horoscope generation
- [x] **TASK_018** (complete) — Testing: add aiogram tests covering all user flows
- [x] **TASK_019** (complete) — Improvement: add more emojis to bot messages and AI-generated text
- [x] **TASK_020** (complete) — Feature: send first horoscope to user after profile setup
