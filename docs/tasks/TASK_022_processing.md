# TASK_022 — Refactor: use async repository methods instead of inline sync_to_async wrappers

**Is task investigated**: yes
**Summary**: Multiple handlers create redundant inline `sync_to_async` wrappers for repository calls, even though all repositories already have async variants (`aget_by_telegram_uid`, `ahas_active_subscription`, etc.). Replace these with direct async method calls to simplify code and reduce overhead.

## Checkboxes

- [x] 1. Replace inline wrappers in `horoscope/handlers/horoscope.py`
- [x] 2. Replace inline wrappers in `horoscope/handlers/subscription.py`
- [x] 3. Replace inline wrappers in `horoscope/handlers/language.py`
- [x] 4. Verify all tests still pass

## Investigation

### Changes Made

1. **horoscope/handlers/horoscope.py**: Replaced `_check_subscription()` sync_to_async wrapper with direct `subscription_repo.ahas_active_subscription()` call. Removed unused `sync_to_async` import.

2. **horoscope/handlers/subscription.py**:
   - Converted `_get_user_language()` sync function to `_aget_user_language()` async function using `aget_by_telegram_uid()`
   - Replaced `_activate()` sync_to_async wrapper with `service.aactivate_subscription()`
   - Removed all inline `@sync_to_async` wrappers
   - Removed unused `sync_to_async` import

3. **horoscope/handlers/language.py**: Replaced `_update_lang()` sync_to_async wrapper with direct `user_profile_repo.aupdate_language()` call. Removed unused `sync_to_async` import.

## Questions
None
