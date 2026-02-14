# TASK_044 - Migrate handlers to use AppContext instead of direct message methods

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Replace all direct `message.answer()`, `message.reply()`, and `bot.send_message()` calls in handlers and Celery tasks with `app_context.send_message()` and related methods. This ensures all outgoing messages are automatically logged to MessageHistory.

## Checklist
- [x] Update `telegram_bot/handlers/start.py` to use app_context
- [x] Update `horoscope/handlers/wizard.py` to use app_context
- [x] Update `horoscope/handlers/horoscope.py` to use app_context
- [x] Update `horoscope/handlers/language.py` to use app_context
- [x] Update `horoscope/handlers/subscription.py` to use app_context
- [x] Update `horoscope/tasks/messaging.py` to use AppContext.for_user()
- [x] Update handler tests to mock/verify app_context usage
- [x] Verify all tests pass

## Investigation

### Changes made
1. All handlers now accept `app_context: AppContext` parameter
2. All `message.answer()` → `app_context.send_message(text=...)`
3. All `callback.message.answer()` → `app_context.send_message(text=...)`
4. All `callback.message.edit_reply_markup(reply_markup=None)` → `app_context.edit_message(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]), message_id=...)`
5. `callback.message.answer_invoice()` → `app_context.send_invoice()`
6. Celery messaging: `bot.send_message()` → `AppContext.for_user(bot, uid).send_message()`
7. Added `send_invoice` method to AppContext
8. Fixed `edit_message` and `send_invoice` to handle `bool` returns from Telegram API (isinstance check)
9. Updated test middleware to inject mock AppContext
10. Updated subscription error test to pass mock app_context

## Questions
_(no questions)_
