# TASK_016 — Testing: unit tests for services and repositories

## Summary

Project has zero tests. Add unit tests for core business logic: zodiac sign calculation, horoscope generation, subscription service, repositories, and entity conversions.

## Checkboxes

- [ ] Create horoscope/tests/test_horoscope_service.py — test zodiac sign calculation (all 12 signs + edge cases on boundaries)
- [ ] Test horoscope text generation determinism (same uid+date = same result)
- [ ] Test teaser extraction (first N lines)
- [ ] Create horoscope/tests/test_subscription_service.py — test activate (new + renewal), cancel, expire_overdue
- [ ] Create core/tests/test_user_repository.py — test get_or_create, update_or_create
- [ ] Create horoscope/tests/test_entities.py — test from_model() conversion for all entities
- [ ] Create config/settings_test.py (referenced in pyproject.toml but missing)
- [ ] Verify tests pass via `make test`
