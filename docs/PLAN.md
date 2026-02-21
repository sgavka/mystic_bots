# PLAN

## Next step

TASK_074 complete. All implementable tasks done. TASK_073 skipped. Running "all tasks complete" workflow.

## Tasks

- [x] **TASK_074** (complete) — Improvement: two-phase teaser sending (daily then periodic)
- [x] **TASK_072** (complete) — Improvement: optimize get_telegram_uids_by_notification_hour query
- [ ] **TASK_073** (waiting_for_clarification / skipped) — Improvement: add offset between generate and send scheduler tasks
- [x] **TASK_071** (complete) — Fix: horoscope generated but not sent to users
- [x] **TASK_069** (complete) — Feature: add /subscribe command for subscription purchase
- [x] **TASK_070** (complete) — Refactor: extract horoscope type into enum (first, daily)
- [x] **TASK_067** (complete) — Refactor: implement separated generation/sending from TASK_066 recommendation
- [x] **TASK_068** (complete) — Feature: per-language UTC time for horoscope generation, user timezone/notification time settings
- [x] **TASK_066** (complete) — Refactor: separate horoscope generation from sending in batch task
- [x] **TASK_063** (complete) — Add Italian and French languages with translations
- [x] **TASK_064** (complete) — Create copies of ad SVG logo in all project languages
- [x] **TASK_065** (complete) — Add Loki logging integration from redgifs_downloader_bot
- [x] **TASK_062** (complete) — Fix: prevent duplicate horoscope sending on service restart
- [x] **TASK_061** (complete) — Refactor: remove Celery from prod, replace tasks with async background execution
- [x] **TASK_056** (complete) — Full test coverage for all handlers
- [x] **TASK_057** (complete) — Add optional birth time to user profile
- [x] **TASK_058** (complete) — Add Hindi and Arabic languages
- [x] **TASK_059** (complete) — Use button instead of text for skipping birth time in wizard
- [x] **TASK_060** (complete) — Add admin handler for stats (new users, horoscopes, subscriptions)

## Completed

- [x] **TASK_055** (complete) — Add missing translations and UX feedback for followup questions
- [x] **TASK_051** (complete) — Feature: allow subscribers to ask questions about horoscope theme
- [x] **TASK_046** (complete) — Exception handling and logging audit
- [x] **TASK_045** (complete) — Add UserLanguageMiddleware for i18n
- [x] **TASK_044** (complete) — Migrate handlers to use AppContext instead of direct message methods

- [x] **TASK_043** (complete) — Extract LoggingMiddleware from UserMiddleware
- [x] **TASK_042** (complete) — Upgrade AppContext with DB logging and add helpers.py
- [x] **TASK_038** (complete) — Refactor: inline remaining text constants in horoscope handlers
- [x] **TASK_039** (complete) — Feature: periodic teaser horoscopes for non-subscribers with configurable intervals
- [x] **TASK_040** (complete) — Feature: make bot understand dates in different formats
- [x] **TASK_041** (complete) — Feature: add message history tracking
- [x] **TASK_036** (complete) — Feature: add LLM usage tracking table (1-to-1 with horoscope) and cost calculation command
- [x] **TASK_037** (complete) — Refactor: remove horoscope.messages module, inline texts where used
- [x] **TASK_031** (complete) — Refactor: remove custom db_table from horoscope models, use Django defaults
- [x] **TASK_032** (complete) — Refactor: move horoscope.config values to config.settings with env vars
- [x] **TASK_033** (complete) — Feature: trigger horoscope generation when user runs /horoscope but horoscope not yet generated
- [x] **TASK_034** (complete) — Refactor: remove horoscope.translations wrapper, use Django gettext directly
- [x] **TASK_035** (complete) — Refactor: make bot languages list configurable via config.settings and env
- [x] **TASK_026** (complete) — Refactor: use Django/aiogram i18n for translations instead of dict
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
