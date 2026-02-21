# TASK_073 - Improvement: add offset between generate and send scheduler tasks

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add an initial delay (offset) to the send_daily_horoscope_notifications scheduler task so it doesn't start at the same time as generate_daily_for_all_users. This prevents a race condition where the send task runs before horoscopes have been generated.

## Checklist
- [ ] Add `initial_delay_seconds` parameter to `BackgroundScheduler.schedule()`
- [ ] Apply initial delay to `send_daily_horoscope_notifications` task (e.g., 5 minutes)
- [ ] Make the offset configurable via environment variable
- [ ] Add tests for the initial delay behavior

## Investigation

**Current behavior:** Both `generate_daily_for_all_users` and `send_daily_horoscope_notifications` start immediately when the bot starts. If generate takes time, the send task may find no horoscopes to send.

**Proposed fix:** Add an optional `initial_delay_seconds` parameter to `BackgroundScheduler.schedule()`. Before the first execution, the task sleeps for the specified delay. This ensures generation completes before sending begins.

**Implementation:**
1. Add `initial_delay_seconds: int = 0` parameter to `schedule()` and `_run_periodic()`
2. In `_run_periodic()`, add `await asyncio.sleep(initial_delay_seconds)` before the main loop
3. Pass delay (e.g., 5 * 60 = 300 seconds) to the send task schedule call
4. Add `SCHEDULER_SEND_OFFSET_SECONDS` env var with default 300

**Note:** Also found a bug on line 112 of start_bot.py: `func=30 * 60` should be `func=send_periodic_teaser_notifications`. This should be fixed as part of this task or separately.

## Questions
- Is the proposed approach (initial delay on send task) acceptable, or would you prefer a different mechanism (e.g., event-based trigger after generation completes)?
- Should the offset also apply to periodic teaser notifications?
- Should the bug on line 112 (`func=30 * 60` instead of `func=send_periodic_teaser_notifications`) be fixed as part of this task?
response: skip this