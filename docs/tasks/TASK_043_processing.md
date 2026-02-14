# TASK_043 - Extract LoggingMiddleware from UserMiddleware

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Extract incoming message logging from UserMiddleware into a separate LoggingMiddleware class, matching the template v1.1.0 pattern. Currently `_log_message` is embedded in UserMiddleware. The template separates concerns: UserMiddleware only handles user creation/update, LoggingMiddleware handles incoming message logging with full raw data and `fix_unserializable_values_in_raw()` sanitization. Also update middleware chain in `telegram_bot/bot.py` to register LoggingMiddleware as a separate middleware (position 4 in chain).

## Checklist
- [x] Create LoggingMiddleware class in `telegram_bot/middlewares/user.py`
- [x] Move `_log_message` logic from UserMiddleware to LoggingMiddleware
- [x] Upgrade logging to store full raw message data (using `message.model_dump()` + `fix_unserializable_values_in_raw()`)
- [x] Remove `_log_message` from UserMiddleware
- [x] Remove `message_history_repository` dependency from UserMiddleware
- [x] Register LoggingMiddleware in `telegram_bot/bot.py:setup_middlewares()`
- [x] Update DI container if needed (not needed — uses container directly)
- [ ] Update tests

## Investigation

### Changes made
1. UserMiddleware: removed `_log_message` method and `message_history_repository` dependency — now only handles user creation/update
2. LoggingMiddleware: new class that logs incoming messages with:
   - Full raw data via `message.model_dump()` + `fix_unserializable_values_in_raw()`
   - Proper from/to user tracking (to_user = bot_id)
   - Dice message text formatting
   - Callback query data extraction
3. bot.py: `setup_middlewares` now takes `bot_instance` parameter; LoggingMiddleware registered as 4th middleware in chain
4. Middleware chain: BotMiddleware → UserMiddleware → AppContextMiddleware → LoggingMiddleware

## Questions
_(no questions)_
