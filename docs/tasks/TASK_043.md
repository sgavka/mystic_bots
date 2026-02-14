# TASK_043 - Extract LoggingMiddleware from UserMiddleware

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Extract incoming message logging from UserMiddleware into a separate LoggingMiddleware class, matching the template v1.1.0 pattern. Currently `_log_message` is embedded in UserMiddleware. The template separates concerns: UserMiddleware only handles user creation/update, LoggingMiddleware handles incoming message logging with full raw data and `fix_unserializable_values_in_raw()` sanitization. Also update middleware chain in `telegram_bot/bot.py` to register LoggingMiddleware as a separate middleware (position 4 in chain).

## Checklist
- [ ] Create LoggingMiddleware class in `telegram_bot/middlewares/user.py`
- [ ] Move `_log_message` logic from UserMiddleware to LoggingMiddleware
- [ ] Upgrade logging to store full raw message data (using `message.model_dump()` + `fix_unserializable_values_in_raw()`)
- [ ] Remove `_log_message` from UserMiddleware
- [ ] Remove `message_history_repository` dependency from UserMiddleware
- [ ] Register LoggingMiddleware in `telegram_bot/bot.py:setup_middlewares()`
- [ ] Update DI container if needed
- [ ] Update tests

## Investigation
_(to be filled during investigation)_

## Questions
_(no questions)_
