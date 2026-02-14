**Is task investigated** — yes
**Commit ID** —
**Summary** — Periodic teaser horoscopes for non-subscribers with configurable intervals and activity window

## Original Requirements

- For users without subscription every N days send horoscope with teaser, but make teaser much bigger than usual
- But for daily horoscope for users without subscription make teaser smaller
- Also send it for users without subscription only next M days after last activity in bot

## Checkboxes

- [ ] Add `last_activity` field to User model + migration
- [ ] Update UserMiddleware to track last activity on every interaction
- [ ] Update UserEntity and UserRepository with new field
- [ ] Add settings: HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS (N), HOROSCOPE_ACTIVITY_WINDOW_DAYS (M), HOROSCOPE_EXTENDED_TEASER_LINE_COUNT
- [ ] Modify teaser generation to support different sizes (small for daily, big for periodic)
- [ ] Create new Celery task for periodic teaser sending (every N days, only active users within M days)
- [ ] Modify daily send task to skip non-subscribers (they get periodic teasers instead)
- [ ] Add tests
- [ ] Update Celery beat schedule

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
   - `HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS` — how often to send periodic teasers to non-subscribers (default: 3)
   - `HOROSCOPE_ACTIVITY_WINDOW_DAYS` — only send to users active within this many days (default: 30)
   - `HOROSCOPE_EXTENDED_TEASER_LINE_COUNT` — teaser size for periodic sends (default: 8)
   - Keep existing `HOROSCOPE_TEASER_LINE_COUNT` for daily/on-demand (make smaller, e.g. 2)

4. **Modify teaser generation** (`horoscope/services/llm.py`, `horoscope/services/horoscope.py`):
   - Store two teasers in Horoscope model or generate extended teaser on-the-fly
   - Option A: Add `extended_teaser_text` field to Horoscope model
   - Option B: Re-slice full_text at send time using extended line count

5. **New Celery task** for periodic teaser:
   - Runs every day, checks if user is due for periodic teaser
   - Filters: no subscription, last_activity within M days, not sent periodic teaser in last N days
   - Sends extended teaser

6. **Daily task modification**:
   - Daily `send_daily_horoscope_notifications_task` should skip non-subscribers (or send smaller teaser)

## Questions

1. Should the daily horoscope still be **generated** for non-subscribers, or only generated when needed for periodic teasers? (Currently all users get horoscopes generated daily)
2. For the periodic teaser: should it use the daily horoscope of that day, or should it generate a fresh one?
3. What are good defaults for N (periodic interval) and M (activity window)?
4. Should we add an `extended_teaser_text` field to the Horoscope model, or generate the extended teaser on-the-fly from `full_text`?
5. Should daily horoscope notifications be completely skipped for non-subscribers, or should they still get the small teaser daily?
