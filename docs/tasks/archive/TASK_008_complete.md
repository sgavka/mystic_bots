# TASK_008 — Daily horoscope: schedule + teaser wall

## Commit ID

0a6c904

## Summary

Set up Celery Beat to trigger daily horoscope generation for all users. Free users see a teaser (first few lines) with a subscription CTA. Subscribers see the full horoscope.

## Checkboxes

- [x] Create `horoscope/tasks/send_daily_horoscope.py` — two tasks: generate + send notifications
- [x] Configure Celery Beat schedule in config/settings.py (CELERY_BEAT_SCHEDULE)
- [x] Teaser logic: free users see teaser_text + subscription CTA, subscribers see full_text
- [x] Create subscription CTA inline keyboard button (callback_data="subscribe")
- [x] Create `horoscope/handlers/horoscope.py` — /horoscope command handler
- [x] Handle users with no profile (prompt to /start)
- [x] Register horoscope router in bot.py
- [ ] Test daily flow end-to-end (requires running services)

## Investigation

Two Celery beat tasks:
1. generate_daily_for_all_users_task: queries all UserProfile records, queues generate_horoscope_task for each
2. send_daily_horoscope_notifications_task: sends messages to users (full or teaser based on subscription)
/horoscope command: checks profile → checks horoscope for today → checks subscription → shows full or teaser
