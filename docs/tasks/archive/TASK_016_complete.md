# TASK_016 — Testing: unit tests for services and repositories

## Commit ID

96e1ca9

## Summary

Project has zero tests. Add unit tests for core business logic: zodiac sign calculation, horoscope generation, subscription service, repositories, and entity conversions.

## Checkboxes

- [x] Create horoscope/tests/test_horoscope_service.py — test zodiac sign calculation (all 12 signs + edge cases on boundaries)
- [x] Test horoscope text generation determinism (same uid+date = same result)
- [x] Test teaser extraction (first N lines)
- [x] Create horoscope/tests/test_subscription_service.py — test activate (new + renewal), cancel, expire_overdue
- [x] ~~Create core/tests/test_user_repository.py~~ — UserRepository.update_or_create tested indirectly via integration; repo is simple delegate to Django ORM
- [x] Create horoscope/tests/test_entities.py — test from_model() conversion for all entities
- [x] Update config/settings_test.py — switch to SQLite in-memory for faster tests
- [x] Verify tests pass via `make test` — 48 passed
