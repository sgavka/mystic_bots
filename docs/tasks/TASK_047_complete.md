# TASK_047 - Increase test coverage for Celery task helpers

## Is task investigated
yes

## Commit ID
a118067

## Branch name
_(none)_

## Summary
Add unit tests for `horoscope/tasks/messaging.py` (15% coverage) and `horoscope/tasks/generate_horoscope.py` (40% coverage) — specifically the `_send_daily_horoscope` and `_send_first_horoscope` helper functions.

## Checklist
- [x] Add tests for `messaging.send_message()` — success and failure paths (4 tests)
- [x] Add tests for `messaging.send_messages_batch()` — full batch, partial failures, empty, with keyboards (4 tests)
- [x] Add tests for `generate_horoscope._send_daily_horoscope()` — subscriber vs non-subscriber, failure, language (4 tests)
- [x] Add tests for `generate_horoscope._send_first_horoscope()` — success, failure, no profile (3 tests)

## Investigation
These functions create Bot instances and use `asyncio.run()` to send messages. Tests should mock `AppContext.for_user()` and `Bot` to avoid real Telegram API calls. The `_send_daily_horoscope` function has branching logic (subscriber gets full text, non-subscriber gets teaser + subscribe button) that should be tested.

## Questions
- Should we prioritize these tests or focus on other improvements first?
yes, these