# TASK_047 - Increase test coverage for Celery task helpers

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add unit tests for `horoscope/tasks/messaging.py` (15% coverage) and `horoscope/tasks/generate_horoscope.py` (40% coverage) — specifically the `_send_daily_horoscope` and `_send_first_horoscope` helper functions.

## Checklist
- [ ] Add tests for `messaging.send_message()` — success and failure paths
- [ ] Add tests for `messaging.send_messages_batch()` — full batch, partial failures
- [ ] Add tests for `generate_horoscope._send_daily_horoscope()` — subscriber vs non-subscriber
- [ ] Add tests for `generate_horoscope._send_first_horoscope()` — success and failure

## Investigation
These functions create Bot instances and use `asyncio.run()` to send messages. Tests should mock `AppContext.for_user()` and `Bot` to avoid real Telegram API calls. The `_send_daily_horoscope` function has branching logic (subscriber gets full text, non-subscriber gets teaser + subscribe button) that should be tested.

## Questions
- Should we prioritize these tests or focus on other improvements first?
