# TASK_023 — Improvement: add error handling to critical user paths

**Is task investigated**: yes
**Commit ID**: be55f7b
**Summary**: Added error handling to critical user paths: profile creation in wizard, subscription activation after payment, and first horoscope delivery logging.

## Checkboxes

- [x] 1. Add try-except in wizard profile creation step (wizard.py)
- [x] 2. Add try-except in successful_payment_handler (subscription.py)
- [x] 3. Improve Celery task exception logging (generate_horoscope.py)
- [x] 4. Add error translation keys to translations.py
- [x] 5. Add tests for error paths

## Investigation

### Changes Made

1. **horoscope/handlers/wizard.py**: Wrapped `_create_profile()` in try-except. On failure: logs exception, clears FSM state, sends translated error message to user, and returns early (no Celery task queued).

2. **horoscope/handlers/subscription.py**: Wrapped `service.aactivate_subscription()` in try-except. On failure: logs exception with payment charge ID for debugging, sends translated error message to user.

3. **horoscope/tasks/generate_horoscope.py**: Added explicit logging when `send_message()` fails in `_send_first_horoscope()`. The `send_message` function already returns False on failure, now we log it.

4. **horoscope/translations.py**: Added two new error translation keys:
   - `error.profile_creation_failed` (4 languages)
   - `error.payment_failed` (4 languages)

5. **horoscope/tests/test_handlers.py**: Added `TestErrorHandling` class with:
   - `test_wizard_profile_creation_failure` — verifies error message and no Celery task queued
   - `test_subscription_activation_failure` — verifies error message sent to user

## Questions
None
