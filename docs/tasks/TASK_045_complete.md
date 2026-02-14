# TASK_045 - Add UserLanguageMiddleware for i18n

## Is task investigated
yes

## Commit ID
a92d478

## Branch name
_(none)_

## Summary
Add `telegram_bot/middlewares/i18n.py` with `UserLanguageMiddleware` that activates Django's translation locale based on user's Telegram `language_code`. Register it as position 5 in the middleware chain.

## Checklist
- [x] Create `telegram_bot/middlewares/i18n.py` with UserLanguageMiddleware
- [x] Configure supported locales from settings (HOROSCOPE_SUPPORTED_LANGUAGE_CODES)
- [x] Register middleware in `telegram_bot/bot.py:setup_middlewares()`
- [x] Verify existing Django gettext translations still work
- [x] Add tests (5 tests covering supported/unsupported/none/region/deactivation)

## Investigation

### Approach
The project uses Django's `gettext` with a custom `translate()` function. Rather than migrating to aiogram's I18n system, we add a middleware that activates Django's locale for each request based on the user's Telegram language_code. This way:
- `gettext_lazy` strings resolve correctly in the user's language
- Existing `translate()` calls continue to work
- No handler changes needed

### Middleware chain (final)
1. BotMiddleware — injects bot_slug
2. UserMiddleware — creates/updates user, injects UserEntity
3. AppContextMiddleware — creates AppContext, injects as 'app_context'
4. LoggingMiddleware — logs incoming messages with full raw data
5. UserLanguageMiddleware — activates Django locale for user's language

## Questions
- Decision: Keep Django gettext and add locale activation in middleware (NOT migrate to aiogram i18n). This avoids rewriting all translation calls.
