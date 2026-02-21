# TASK_071 - Fix: horoscope generated but not sent to users

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Horoscopes are being generated but not sent due to a race condition between the generate and send tasks, combined with hour-based filtering in the send task.

## Checklist
- [ ] Fix `send_daily_horoscope_notifications` to find unsent horoscopes regardless of current hour
- [ ] Fix `send_periodic_teaser_notifications` to find unsent horoscopes regardless of current hour
- [ ] Add tests for the fix
- [ ] Update PLAN.md

## Investigation

### Root Cause: Race condition + hour-based filtering

**Two problems work together to cause the bug:**

1. **Race condition on concurrent startup**: Both `generate_daily_for_all_users` and `send_daily_horoscope_notifications` are scheduled as concurrent asyncio tasks. On each run:
   - Generate task starts → calls LLM → takes N minutes to create horoscopes
   - Send task starts AT THE SAME TIME → finds no horoscopes → finishes immediately
   - Both then sleep for 1 hour

2. **Hour drift**: After the initial run, tasks wake up at slightly different times. Since both filter users by `timezone.now().hour`, the send task at hour=2 looks for users with `notification_hour_utc=2`, completely missing horoscopes generated at hour=1.

**Example timeline (Hindi users, notification_hour=1 UTC):**
- 01:00 - Both tasks run
- 01:00 - Send task: no horoscopes for hour=1 users → nothing to send, sleeps 1h
- 01:12 - Generate task: finishes generating horoscope for Hindi users
- 01:12 - Generate task sleeps 1h
- 02:00 - Send task wakes: `timezone.now().hour = 2`, queries users with hour=2 → Hindi users NOT included
- **Result**: Hindi horoscope generated at 01:12 with `sent_at = NULL` forever

The same issue affects `send_periodic_teaser_notifications`.

### Fix Approach

**Change the send tasks to query ALL unsent horoscopes for today**, instead of filtering by current hour. The hour-based filtering only makes sense for generation (to spread LLM load). For sending, we should send any horoscope that exists and hasn't been sent yet.

Specifically:
- `send_daily_horoscope_notifications`: Query all user profiles, check for unsent daily horoscopes for today, send to subscribers
- `send_periodic_teaser_notifications`: Same approach, send to non-subscribers

This decouples the sending from the current UTC hour, making it a "catch-up" mechanism that picks up any generated-but-unsent horoscopes.

## Questions
_(no questions)_
