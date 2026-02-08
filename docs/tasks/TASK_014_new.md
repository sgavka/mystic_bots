# TASK_014 — Feature: subscription expiry reminders

## Summary

Users are not notified when their subscription is about to expire or has expired. Add a Celery beat task that sends reminders before expiry and a notification after expiry.

## Checkboxes

- [ ] Create horoscope/tasks/subscription_reminders.py with Celery tasks
- [ ] Task 1: send_expiry_reminders_task — notify users whose subscription expires within N days (e.g. 3 days)
- [ ] Task 2: send_expired_notifications_task — notify users whose subscription just expired (run after expire_overdue)
- [ ] Add tasks to CELERY_BEAT_SCHEDULE in config/settings.py
- [ ] Add reminder message text with re-subscribe button (InlineKeyboardMarkup with callback_data="subscribe")
- [ ] Track reminded users to avoid duplicate reminders (flag in Subscription model or separate tracking)
