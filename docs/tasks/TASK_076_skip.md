# TASK_076 - Refactor: extract user language helper and standardize fallback pattern

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Multiple files repeat the same pattern for getting user language from profile:
```python
profile = await user_profile_repo.aget_by_telegram_uid(telegram_uid)
lang = profile.preferred_language if profile else 'en'
```

This appears in send_daily_horoscope.py, send_periodic_teaser.py, subscription_reminders.py, and generate_horoscope.py. Additionally, the fallback pattern is inconsistent (`if profile else 'en'` vs `or 'en'`).

Proposed fix: add a repository method `aget_user_language(telegram_uid) -> str` that returns the language directly with 'en' fallback, or extract a shared helper function.

## Checklist
- [ ] Create helper or repo method for user language lookup
- [ ] Replace all duplicate patterns
- [ ] Standardize fallback to consistent pattern
- [ ] Add tests

## Investigation
_(not yet investigated)_

## Questions
- Prefer a repository method (`aget_user_language`) or a standalone helper function?
