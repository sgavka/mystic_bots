# TASK_025 — Refactor: consistent language retrieval across handlers

**Is task investigated**: yes
**Commit ID**: (pending)
**Summary**: Language retrieval was inconsistent across handlers. Some used inline lookups with hardcoded 'en' fallback, subscription.py had a private `_aget_user_language()` helper. Created shared `aget_user_language()` utility and replaced hardcoded 'en' fallbacks with `map_telegram_language(user.language_code)`.

## Checkboxes

- [x] 1. Create shared `aget_user_language()` async utility
- [x] 2. Update horoscope.py handler
- [x] 3. Update subscription.py handler
- [x] 4. Update language.py handler (error fallback paths)
- [x] 5. Verify all tests pass

## Investigation

### Changes Made

1. **horoscope/handlers/utils.py** (NEW): Created shared async utility `aget_user_language(user)` that fetches profile and returns `preferred_language`, falling back to `map_telegram_language(user.language_code)` instead of hardcoded 'en'.

2. **horoscope/handlers/horoscope.py**: Replaced hardcoded `'en'` in no-profile fallback with `map_telegram_language(user.language_code)`.

3. **horoscope/handlers/subscription.py**: Removed private `_aget_user_language()` helper, replaced with shared `aget_user_language()` from utils. Removed unused `container` import.

4. **horoscope/handlers/language.py**: Replaced both hardcoded `'en'` fallbacks (in `language_command_handler` and `change_language_callback`) with `map_telegram_language(user.language_code)`.

### Design Decision

Handlers that already fetch the profile (horoscope.py, language.py) use `map_telegram_language(user.language_code)` directly as the fallback — avoids redundant DB query. The shared `aget_user_language()` utility is for handlers that only need the language (subscription.py).

## Questions
None
