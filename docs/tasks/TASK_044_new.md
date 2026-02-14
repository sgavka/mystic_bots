# TASK_044 - Migrate handlers to use AppContext instead of direct message methods

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Replace all direct `message.answer()`, `message.reply()`, and `bot.send_message()` calls in handlers and Celery tasks with `app_context.send_message()` and related methods. This ensures all outgoing messages are automatically logged to MessageHistory. Files affected: `horoscope/handlers/wizard.py`, `horoscope/handlers/horoscope.py`, `horoscope/handlers/language.py`, `horoscope/handlers/subscription.py`, `horoscope/tasks/messaging.py`, `telegram_bot/handlers/start.py`.

## Checklist
- [ ] Update `telegram_bot/handlers/start.py` to use app_context
- [ ] Update `horoscope/handlers/wizard.py` to use app_context
- [ ] Update `horoscope/handlers/horoscope.py` to use app_context
- [ ] Update `horoscope/handlers/language.py` to use app_context
- [ ] Update `horoscope/handlers/subscription.py` to use app_context
- [ ] Update `horoscope/tasks/messaging.py` to use AppContext.for_user()
- [ ] Update handler tests to mock/verify app_context usage
- [ ] Verify all tests pass

## Investigation
_(to be filled during investigation)_

## Questions
_(no questions)_
