# TASK_013 — Improvement: error handling and Celery retry logic

## Summary

Celery tasks have no retry mechanism, send_daily_horoscope creates a new Bot instance per message (no session reuse), and asyncio.run() inside Celery is fragile. Add retry decorators, fix bot session management, and improve error handling throughout.

## Checkboxes

- [ ] Add Celery retry with exponential backoff to generate_horoscope_task
- [ ] Add Celery retry to send_daily_horoscope_notifications_task
- [ ] Fix _send_message_sync() — reuse Bot session instead of creating new Bot per message
- [ ] Fix asyncio.run() usage in Celery tasks — use asgiref sync_to_async or proper async Celery
- [ ] Add error handling for missing UserProfile during horoscope generation (notify user or skip gracefully)
- [ ] Add startup validation for required env vars (BOT token, DB, Redis) in config/settings.py
- [ ] Ensure DEBUG=False by default in settings.py (only True when DJANGO_DEBUG=true is explicit)
