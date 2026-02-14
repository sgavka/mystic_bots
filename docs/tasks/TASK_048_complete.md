# TASK_048 - Increase test coverage for AppContext and middlewares

## Is task investigated
yes

## Commit ID
_(pending)_

## Branch name
_(none)_

## Summary
Increase test coverage for `telegram_bot/app_context.py` (73% — missing `for_user`, `send_invoice`, `send_dice`, `set_reaction`) and `telegram_bot/middlewares/i18n.py` (73% — missing Update/CallbackQuery event types).

## Checklist
- [x] Add tests for `AppContext.for_user()` factory method (1 test)
- [x] Add tests for `AppContext.send_invoice()` — success, non-Message return (2 tests)
- [x] Add tests for `AppContext.send_dice()` — default and custom emoji (2 tests)
- [x] Add tests for `AppContext.set_reaction()` — success, failure, custom emoji (3 tests)
- [x] Add tests for `UserLanguageMiddleware` handling `CallbackQuery` and `Update` events (4 tests)

## Investigation
`AppContext.for_user()` is a classmethod that creates an instance without bot.id — needs a test verifying it works with mocked Bot. The `send_invoice/send_dice/set_reaction` methods follow the same pattern as `send_message` but have their own DB logging logic. The i18n middleware has branches for CallbackQuery and Update event types that aren't covered.

## Questions
- Should we add these tests or are the current 274 tests sufficient for now?
add these tests