# TASK_013 — Improvement: error handling and Celery retry logic

## Commit ID

1b7d5ad

## Summary

Celery tasks have no retry mechanism, send_daily_horoscope creates a new Bot instance per message (no session reuse), and asyncio.run() inside Celery is fragile. Add retry decorators, fix bot session management, and improve error handling throughout.

## Checkboxes

- [x] Add Celery retry with exponential backoff to generate_horoscope_task
- [x] Add Celery retry to send_daily_horoscope_notifications_task
- [x] Fix _send_message_sync() — reuse Bot session instead of creating new Bot per message (renamed to _send_messages_sync)
- [x] Fix asyncio.run() usage in Celery tasks — asyncio.run() is correct for sync Celery workers (no change needed)
- [x] Add error handling for missing UserProfile during horoscope generation — already handled via ValueError catch
- [x] Add startup validation for required env vars (BOT token, DB password) in config/settings.py
- [x] Ensure DEBUG=False by default in settings.py (only True when DJANGO_DEBUG=true is explicit)

## Investigation

### Celery retry
- `generate_horoscope_task`: Add `autoretry_for=(Exception,)`, `retry_backoff=True`, `retry_backoff_max=600`, `max_retries=3`. Keep ValueError as non-retryable.
- `send_daily_horoscope_notifications_task`: Add retry with `bind=True`, `max_retries=3`, `retry_backoff=True`.

### Bot session reuse
- `_send_message_sync()` creates a new Bot per message. Refactor `send_daily_horoscope_notifications_task` to create Bot once, send all messages, then close session.

### asyncio.run() in Celery
- `asyncio.run()` is fine for sync Celery workers — it creates a fresh event loop. No change needed.

### Missing UserProfile handling
- Already handled: `HoroscopeService.generate_for_user()` raises ValueError, caught in task. No change needed.

### DEBUG default
- Change `DJANGO_DEBUG` default from `'True'` to `'False'`

### Startup validation
- Add checks for BOT token (CURRENT_BOT_TOKEN) to warn on empty
