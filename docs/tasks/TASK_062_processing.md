# TASK_062 - Fix duplicate horoscope sending on service restart

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Prevent `send_daily_horoscope_notifications` and `send_periodic_teaser_notifications` from sending horoscopes that were already sent. On service restart, the scheduler runs immediately, re-sending horoscopes to all users.

## Checklist
- [x] Add `sent_at` check in `send_daily_horoscope_notifications`
- [x] Add `sent_at` check in `send_periodic_teaser_notifications`
- [ ] Add/update tests
- [ ] Verify tests pass

## Investigation
**Root cause**: Both sending tasks fetch today's horoscope and send it without checking if `horoscope.sent_at` is already set. When the service restarts, the scheduler immediately runs all tasks again, causing duplicate sends.

**Fix**: After fetching the horoscope, check `if horoscope.sent_at is not None: continue` to skip already-sent horoscopes.

**Affected files**:
- `horoscope/tasks/send_daily_horoscope.py` — `send_daily_horoscope_notifications()`
- `horoscope/tasks/send_periodic_teaser.py` — `send_periodic_teaser_notifications()`

## Questions
_(no questions)_
