# TASK_075 - Improvement: batch queries in background tasks to fix N+1 problem

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Background tasks (send_daily_horoscope, send_periodic_teaser, subscription_reminders, generate_daily) execute N+1 queries: they loop through users and call individual repo methods per user (subscription check, profile lookup, horoscope fetch, mark_sent). For 10 users this means 40+ queries.

Proposed fix: add batch repository methods that fetch data for multiple users in a single query (e.g. `aget_active_subscription_uids(telegram_uids)`, `aget_profiles_by_telegram_uids(telegram_uids)`), then use these in the task loops.

## Checklist
- [ ] Investigate and list all N+1 patterns in tasks
- [ ] Add batch repository methods
- [ ] Refactor tasks to use batch queries
- [ ] Add tests for batch methods
- [ ] Verify performance improvement

## Investigation
_(not yet investigated)_

## Questions
- Is this a priority given the current user count? If there are few users, the N+1 is negligible.
- Should we batch all tasks or start with the most critical one (send_periodic_teaser)?
