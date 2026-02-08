# TASK_004 — Horoscope app: models

## Commit ID

*(pending)*

## Summary

Create the `horoscope` Django app with models for UserProfile (name, birth date, birth place, living place), Horoscope (generated content, date, user), and Subscription (status, expiry, user).

## Checkboxes

- [x] Create `horoscope/models.py` — UserProfile, Horoscope, Subscription
- [x] Create `horoscope/entities.py` — Pydantic entities for each model
- [x] Create `horoscope/enums.py` — SubscriptionStatus, HoroscopeType
- [x] Create `horoscope/repositories/` — UserProfileRepository, HoroscopeRepository, SubscriptionRepository
- [x] Create `horoscope/exceptions.py`
- [x] Create migrations (0001_initial)
- [x] Update DI container with horoscope repositories
- [ ] Write basic model tests (deferred to later)

## Investigation

Models:
- **UserProfile**: PK = user_telegram_uid (BigIntegerField), name, date_of_birth, place_of_birth, place_of_living
- **Horoscope**: AutoField PK, user FK, type (daily/first), date, full_text, teaser_text
- **Subscription**: AutoField PK, unique user_telegram_uid, status (active/expired/cancelled), started_at, expires_at
