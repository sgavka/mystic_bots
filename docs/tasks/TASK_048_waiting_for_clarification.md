# TASK_048 - Increase test coverage for AppContext and middlewares

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Increase test coverage for `telegram_bot/app_context.py` (73% — missing `for_user`, `send_invoice`, `send_dice`, `set_reaction`) and `telegram_bot/middlewares/i18n.py` (73% — missing Update/CallbackQuery event types).

## Checklist
- [ ] Add tests for `AppContext.for_user()` factory method
- [ ] Add tests for `AppContext.send_invoice()` — success, bool return, logging
- [ ] Add tests for `AppContext.send_dice()` and `AppContext.set_reaction()`
- [ ] Add tests for `UserLanguageMiddleware` handling `CallbackQuery` and `Update` events

## Investigation
`AppContext.for_user()` is a classmethod that creates an instance without bot.id — needs a test verifying it works with mocked Bot. The `send_invoice/send_dice/set_reaction` methods follow the same pattern as `send_message` but have their own DB logging logic. The i18n middleware has branches for CallbackQuery and Update event types that aren't covered.

## Questions
- Should we add these tests or are the current 274 tests sufficient for now?
add these tests