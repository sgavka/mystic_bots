# TASK_046 - Exception handling and logging audit

## Is task investigated
yes

## Commit ID
b5e4af1

## Branch name
_(none)_

## Summary
Audit all exception handling across the project to align with template v1.1.0 rules: no bare `except Exception` without justification comment, always use `exc_info=e` or `exc_info=True` in logging calls within exception handlers, only catch specific expected exception types. Review all `try/except` blocks and fix violations.

## Checklist
- [x] Audit all `except Exception` catches — add justification comments or replace with specific exception types
- [x] Audit all `logger.error/warning/exception` calls — ensure exc_info is included
- [x] Check for bare `except:` blocks
- [x] Fix any violations found
- [x] Verify all tests pass after changes

## Investigation

### Files audited and violations found

1. **horoscope/handlers/subscription.py:89** — `except Exception` without justification comment
   - Fix: Added comment explaining why broad catch is needed (payment succeeded but DB activation failed)
   - Note: Already uses `logger.exception()` which includes traceback — OK

2. **horoscope/handlers/wizard.py:215** — `except Exception` without justification comment
   - Fix: Added comment explaining why broad catch is needed (profile creation failure)
   - Note: Already uses `logger.exception()` which includes traceback — OK

3. **horoscope/services/horoscope.py:346** — `except Exception as e` missing `exc_info` + no justification
   - Fix: Added `exc_info=e` to `logger.warning()` and added justification comment (LLM fallback)

4. **horoscope/tasks/messaging.py:36** — `except Exception as e` missing `exc_info` + no justification
   - Fix: Added `exc_info=e` to `logger.error()` and added justification comment (Telegram API errors)

5. **horoscope/tasks/messaging.py:81** — `except Exception as e` missing `exc_info` + no justification
   - Fix: Added `exc_info=e` to `logger.error()` and added justification comment (batch loop protection)

6. **horoscope/tasks/generate_horoscope.py:65** — `except ValueError as e` missing `exc_info`
   - Fix: Added `exc_info=e` to `logger.error()`
   - Note: This catches a specific exception (ValueError) — no justification comment needed

### Files verified as correct (no violations)
- `telegram_bot/handlers/errors.py` — Uses `exc_info=event.exception` correctly
- `telegram_bot/middlewares/user.py` — No try/except blocks
- `telegram_bot/middlewares/i18n.py` — try/finally only (no except)

## Questions
_(no questions)_
