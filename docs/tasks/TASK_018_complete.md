## Commit ID

20bf494

## Summary

Add aiogram handler tests using aiogram-test-framework covering all user flows.

## Checkboxes

- [x] Wizard /start handler (new user, returning user)
- [x] Wizard name validation
- [x] Wizard date of birth validation
- [x] Wizard place of birth validation
- [x] Wizard place of living + profile creation
- [x] Complete wizard flow (happy path)
- [x] Horoscope view handler (no profile, no horoscope, subscriber, non-subscriber)
- [x] Subscribe callback handler
- [x] Tests pass

## Investigation

### Approach

Use `aiogram-test-framework` with:
- `TestClient.create()` to create a test client with mock bot
- `MockUserMiddleware` to inject `UserEntity` from test user data (bypasses real DB)
- `dependency_injector` provider overrides to mock repositories
- Celery task `.delay()` patched to avoid real task execution

### Test flows

1. **Wizard flow**: /start → name → DOB → place of birth → place of living → profile created + horoscope queued
2. **Wizard validation**: invalid name, invalid DOB format, future DOB, short city names
3. **Horoscope view**: no profile, no horoscope today, subscriber (full text), non-subscriber (teaser)
4. **Subscription**: subscribe callback → invoice info

### Files

- `horoscope/tests/test_handlers.py` — new test file
