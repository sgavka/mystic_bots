# TASK_042 - Upgrade AppContext with DB logging and add helpers.py

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Upgrade AppContext to match template v1.1.0 pattern: move from `telegram_bot/utils/context.py` to `telegram_bot/app_context.py`, add automatic outgoing message logging to MessageHistory via repository, add `telegram_bot/helpers.py` with `fix_unserializable_values_in_raw()` helper. Currently AppContext is a simple wrapper that doesn't log outgoing messages to DB.

## Checklist
- [ ] Create `telegram_bot/helpers.py` with `fix_unserializable_values_in_raw()` function
- [ ] Move AppContext from `telegram_bot/utils/context.py` to `telegram_bot/app_context.py`
- [ ] Add DI injection of MessageHistoryRepository to AppContext.__init__
- [ ] Add `_log_message_to_db()` method that logs outgoing messages with raw data sanitization
- [ ] Add `for_user()` class method factory for background task usage
- [ ] Add conversation tracking (save/get message_id per conversation)
- [ ] Update all imports across the project (handlers, tasks, middlewares)
- [ ] Remove old `telegram_bot/utils/context.py` file
- [ ] Update tests

## Investigation
_(to be filled during investigation)_

## Questions
_(no questions)_
