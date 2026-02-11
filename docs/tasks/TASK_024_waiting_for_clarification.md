# TASK_024 — Refactor: extract shared message-sending utility for Celery tasks

**Is task investigated**: no
**Summary**: Three Celery task files (`generate_horoscope.py`, `send_daily_horoscope.py`, `subscription_reminders.py`) each have their own message-sending function that creates a Bot instance, sends messages, and closes the session. Extract into a shared utility.

## Checkboxes

- [ ] 1. Create `horoscope/tasks/messaging.py` with shared send functions
- [ ] 2. Refactor `generate_horoscope.py` to use shared utility
- [ ] 3. Refactor `send_daily_horoscope.py` to use shared utility
- [ ] 4. Refactor `subscription_reminders.py` to use shared utility
- [ ] 5. Verify all tests pass

## Investigation

Not yet investigated.

## Questions
None
