# TASK_014 — Feature: subscription expiry reminders

## Commit ID

d832ed8

## Summary

Users are not notified when their subscription is about to expire or has expired. Add a Celery beat task that sends reminders before expiry and a notification after expiry.

## Checkboxes

- [x] Create horoscope/tasks/subscription_reminders.py with Celery tasks
- [x] Task 1: send_expiry_reminders_task — notify users whose subscription expires within N days (3 days)
- [x] Task 2: send_expired_notifications_task — notify users whose subscription just expired (runs expire_overdue first)
- [x] Add tasks to CELERY_BEAT_SCHEDULE in config/settings.py
- [x] Add reminder message text with re-subscribe button (subscribe_keyboard from keyboards.py)
- [x] Track reminded users to avoid duplicate reminders (reminder_sent_at field on Subscription model)

## Investigation

### Model changes
- Add `reminder_sent_at` (DateTimeField, null) to Subscription model — set when reminder is sent, prevents duplicate reminders
- Need a migration

### Config additions
- `SUBSCRIPTION_REMINDER_DAYS = 3` in horoscope/config.py

### New repository methods
- `SubscriptionRepository.get_expiring_soon(days)` — active subs expiring within N days, where reminder_sent_at is null
- `SubscriptionRepository.get_recently_expired()` — subs that expired (status=expired) and reminder_sent_at is null
- `SubscriptionRepository.mark_reminded(subscription_ids)` — bulk update reminder_sent_at

### Tasks
- `send_expiry_reminders_task`: Query expiring-soon, send reminder with subscribe keyboard, mark reminded
- `send_expired_notifications_task`: Run after expire_overdue, query recently expired, send notification, mark reminded

### Bot session reuse
- Use same pattern as _send_messages_sync from send_daily_horoscope.py
