**Is task investigated** — yes
**Commit ID** — (pending)
**Summary** — Periodic teaser horoscopes for non-subscribers with configurable intervals and activity window

## Original Requirements

- For users without subscription every N days send horoscope with teaser, but make teaser much bigger than usual
- But for daily horoscope for users without subscription make teaser smaller
- Also send it for users without subscription only next M days after last activity in bot

## Checkboxes

- [x] Add `last_activity` field to User model + migration
- [x] Update UserMiddleware to track last activity on every interaction
- [x] Update UserEntity and UserRepository with new field
- [x] Add settings: HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS (N=10), HOROSCOPE_ACTIVITY_WINDOW_DAYS (M=5), HOROSCOPE_EXTENDED_TEASER_LINE_COUNT (8)
- [x] Modify teaser generation to support different sizes (small for daily, big for periodic)
- [x] Create new Celery task for periodic teaser sending (every N days, only active users within M days)
- [x] Modify daily send task to skip non-subscribers (they get periodic teasers instead)
- [x] Modify daily generation task to skip non-subscribers without recent activity
- [x] Add `extended_teaser_text` field to Horoscope model
- [x] Add tests (11 new tests)
- [x] Update Celery beat schedule

## Investigation

### Current State
- Daily horoscopes generated for ALL users every 24 hours
- Non-subscribers receive teaser (3 lines, `HOROSCOPE_TEASER_LINE_COUNT=3`) + subscribe link
- Subscribers receive full horoscope
- No `last_activity` tracking on User model
- Teaser size is single setting (`HOROSCOPE_TEASER_LINE_COUNT`)

### Implementation Plan

1. **Add `last_activity` to User model** (`core/models.py`):
   - `last_activity = models.DateTimeField(null=True, blank=True)`
   - Update `UserEntity`, `UserRepository`

2. **Track activity in UserMiddleware** (`telegram_bot/middlewares/user.py`):
   - Set `last_activity=now()` on every message/callback in `update_or_create_user()`

3. **New settings** (`config/settings.py`):
   - `HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS` — how often to send periodic teasers to non-subscribers (default: 10)
   - `HOROSCOPE_ACTIVITY_WINDOW_DAYS` — only send to users active within this many days (default: 5)
   - `HOROSCOPE_EXTENDED_TEASER_LINE_COUNT` — teaser size for periodic sends (default: 8)

4. **Modify teaser generation** (`horoscope/services/llm.py`, `horoscope/services/horoscope.py`):
   - Added `extended_teaser_text` field to Horoscope model
   - Both template and LLM generators now produce regular teaser + extended teaser

5. **New Celery task** for periodic teaser:
   - `send_periodic_teaser_notifications_task` runs daily
   - Filters: no subscription, last_activity within M days, not sent in last N days
   - Sends extended teaser with subscribe link

6. **Daily task modification**:
   - `send_daily_horoscope_notifications_task` now only sends to subscribers
   - `generate_daily_for_all_users_task` now skips non-subscribers without recent activity

## Questions

1. Should the daily horoscope still be **generated** for non-subscribers, or only generated when needed for periodic teasers? (Currently all users get horoscopes generated daily)
daily must be generated next M days after last activity in bot of users without subscription
for users with subscription, send daily horoscope
2. For the periodic teaser: should it use the daily horoscope of that day, or should it generate a fresh one?
use horoscope of that day
3. What are good defaults for N (periodic interval) and M (activity window)?
N = 10, M = 5
4. Should we add an `extended_teaser_text` field to the Horoscope model, or generate the extended teaser on-the-fly from `full_text`?
add field
5. Should daily horoscope notifications be completely skipped for non-subscribers, or should they still get the small teaser daily?
look at question 1
