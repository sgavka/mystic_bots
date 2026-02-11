# TASK_024 — Refactor: extract shared message-sending utility for Celery tasks

**Is task investigated**: yes
**Commit ID**: (pending)
**Summary**: Three Celery task files (`generate_horoscope.py`, `send_daily_horoscope.py`, `subscription_reminders.py`) each had their own message-sending function that creates a Bot instance, sends messages, and closes the session. Extracted into a shared `horoscope/tasks/messaging.py` utility.

## Checkboxes

- [x] 1. Create `horoscope/tasks/messaging.py` with shared send functions
- [x] 2. Refactor `generate_horoscope.py` to use shared utility
- [x] 3. Refactor `send_daily_horoscope.py` to use shared utility
- [x] 4. Refactor `subscription_reminders.py` to use shared utility
- [x] 5. Verify all tests pass

## Investigation

### Changes Made

1. **horoscope/tasks/messaging.py** (NEW): Created shared messaging module with:
   - `send_message(telegram_uid, text, reply_markup)` — sends a single Telegram message via asyncio.run()
   - `send_messages_batch(messages)` — sends multiple messages reusing a single Bot session

2. **horoscope/tasks/generate_horoscope.py**: Replaced inline `_send_first_horoscope()` Bot creation/asyncio.run with `send_message()` from messaging.py

3. **horoscope/tasks/send_daily_horoscope.py**: Removed `_send_messages_sync()` function, replaced with `send_messages_batch()` from messaging.py

4. **horoscope/tasks/subscription_reminders.py**: Removed `_send_messages_with_keyboard()` function from both tasks, replaced with `send_messages_batch()` from messaging.py

5. **horoscope/tests/test_translations.py**: Updated 4 mock patch paths from old private functions to `horoscope.tasks.messaging.send_messages_batch`

## Questions
None
