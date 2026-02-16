# TASK_056 - Full test coverage for all handlers

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
All handlers must be fully covered by tests (like horoscope/tests/test_handlers.py).

## Checklist
- [x] Audit existing handler test coverage
- [ ] Add tests for horoscope/handlers/subscription.py (pre_checkout_handler, successful_payment happy path)
- [ ] Add tests for horoscope/handlers/utils.py (aget_user_language)
- [ ] Add tests for telegram_bot/handlers/errors.py (error_handler)
- [ ] Add tests for telegram_bot/handlers/start.py (start_handler)
- [ ] Ensure all tests pass

## Investigation

### Current Coverage Audit

**Fully tested handlers:**
- horoscope/handlers/admin.py — 4 tests (test_admin.py)
- horoscope/handlers/followup.py — 9 tests (test_followup.py)
- horoscope/handlers/horoscope.py — 5 tests (test_handlers.py)
- horoscope/handlers/language.py — 3 tests (test_handlers.py)
- horoscope/handlers/wizard.py — 19 tests (test_handlers.py)

**Gaps found:**
1. `horoscope/handlers/subscription.py::pre_checkout_handler()` — NOT TESTED
2. `horoscope/handlers/subscription.py::successful_payment_handler()` — only failure path tested, missing happy path
3. `horoscope/handlers/utils.py::aget_user_language()` — NOT TESTED
4. `telegram_bot/handlers/errors.py::error_handler()` — NOT TESTED
5. `telegram_bot/handlers/start.py::start_handler()` — NOT TESTED (note: may be unreachable if wizard router is registered first)

### Implementation Plan
1. Add pre_checkout and successful_payment tests to test_handlers.py
2. Add aget_user_language test to test_handlers.py or a new test file
3. Add telegram_bot handler tests in telegram_bot/tests/test_handlers.py

## Questions
_(no questions)_
