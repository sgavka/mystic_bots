# TASK_042 - Upgrade AppContext with DB logging and add helpers.py

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Upgrade AppContext to match template v1.1.0 pattern: move from `telegram_bot/utils/context.py` to `telegram_bot/app_context.py`, add automatic outgoing message logging to MessageHistory via repository, add `telegram_bot/helpers.py` with `fix_unserializable_values_in_raw()` helper. Currently AppContext is a simple wrapper that doesn't log outgoing messages to DB.

## Checklist
- [x] Create `telegram_bot/helpers.py` with `fix_unserializable_values_in_raw()` function
- [x] Move AppContext from `telegram_bot/utils/context.py` to `telegram_bot/app_context.py`
- [x] Add DI injection of MessageHistoryRepository to AppContext.__init__
- [x] Add `_log_message_to_db()` method that logs outgoing messages with raw data sanitization
- [x] Add `for_user()` class method factory for background task usage
- [x] Add conversation tracking (save/get message_id per conversation)
- [x] Update all imports across the project (handlers, tasks, middlewares)
- [x] Remove old `telegram_bot/utils/context.py` file
- [x] Update tests

## Investigation

### Current state
- AppContext lives at `telegram_bot/utils/context.py` — minimal wrapper with send_message, edit_message, delete_message
- Only import is in `telegram_bot/middlewares/user.py` (AppContextMiddleware) — lazy import
- Container already has `message_history_repository` at `container.core.message_history_repository`
- MessageHistoryRepository has both sync/async `log_message`/`alog_message` methods

### Implementation plan
1. Create `telegram_bot/helpers.py` with `fix_unserializable_values_in_raw()` — recursive datetime→isoformat converter for JSON storage
2. Create `telegram_bot/app_context.py` based on template, adapted for this project's container structure:
   - DI uses `ApplicationContainer.core.message_history_repository` (not `telegram_bot` sub-container)
   - Keep existing methods + add template methods (conversation tracking, send_photo, send_video, send_dice, set_reaction, deletion queue)
   - `_log_message_to_db()` uses sync_to_async wrapper calling `message_history_repo.log_message()`
   - bot_id from `bot.id` for outgoing message tracking
3. Update AppContextMiddleware import from `telegram_bot.utils.context` → `telegram_bot.app_context`
4. Delete old `telegram_bot/utils/context.py`
5. Add tests for helpers.py and AppContext

### Note on TASK_044
Handler migration (message.answer → app_context.send_message) is TASK_044's scope. This task only upgrades AppContext itself.

## Questions
_(no questions)_
