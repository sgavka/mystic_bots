# TASK_045 - Add UserLanguageMiddleware for i18n

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add `telegram_bot/middlewares/i18n.py` with `UserLanguageMiddleware` that uses aiogram's built-in `I18nMiddleware` to set locale from user's Telegram `language_code`. Currently the project uses Django's `gettext_lazy` throughout but has no middleware to automatically activate the correct locale per request. The template provides a middleware that maps Telegram language codes to supported locales and falls back to a default. Register it as position 5 in the middleware chain.

## Checklist
- [ ] Create `telegram_bot/middlewares/i18n.py` with UserLanguageMiddleware
- [ ] Configure supported locales and default locale from settings
- [ ] Register middleware in `telegram_bot/bot.py:setup_middlewares()`
- [ ] Verify existing Django gettext translations still work with aiogram i18n
- [ ] Add tests

## Investigation
_(to be filled during investigation)_

## Questions
- The project currently uses Django's `gettext_lazy` everywhere. Should we keep Django gettext and just add locale activation in the middleware, or migrate to aiogram's i18n system? Need to check compatibility.
