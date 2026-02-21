# TASK_073 - Improvement: add offset between generate and send scheduler tasks

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
While TASK_071 fixed the main bug (send tasks now query all unsent horoscopes regardless of hour), the generate and send tasks still run concurrently on startup. Adding a configurable delay for the send task would ensure horoscopes are generated before the first send attempt, reducing unnecessary empty runs.

## Checklist
- [ ] Add `initial_delay_seconds` parameter to `BackgroundScheduler.schedule()`
- [ ] Configure send tasks with a delay (e.g., 10 minutes after startup)
- [ ] Add tests

## Investigation

**Current behavior:** Both tasks start immediately on bot startup, then repeat every hour. The send task runs before any horoscopes are generated, wasting the first cycle.

**Proposed fix:** Add an `initial_delay_seconds` parameter to `BackgroundScheduler.schedule()`:
```python
async def _run_periodic(self, func, interval_seconds, name, initial_delay_seconds=0):
    if initial_delay_seconds > 0:
        await asyncio.sleep(initial_delay_seconds)
    while True:
        ...
```

Then schedule send tasks with a 10-minute initial delay:
```python
self._scheduler.schedule(
    func=send_daily_horoscope_notifications,
    interval_seconds=hourly_interval,
    initial_delay_seconds=600,  # Wait 10 min for generation to complete
    name="send-daily-horoscope-notifications",
)
```

This is a minor optimization since TASK_071 already ensures unsent horoscopes are picked up on subsequent runs. The main benefit is reducing the window where generated horoscopes sit unsent.

## Questions
- Is this worth implementing given TASK_071 already fixes the core issue? The only benefit is reducing the delay before first send after bot restart.
