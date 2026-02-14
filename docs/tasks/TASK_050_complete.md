# TASK_050 - Fix direct User model access in Celery tasks

## Is task investigated
yes

## Commit ID
17b612a

## Branch name
_(none)_

## Summary
Replace direct `User.objects.get()` calls in `horoscope/tasks/send_daily_horoscope.py` and `horoscope/tasks/send_periodic_teaser.py` with repository methods.

## Checklist
- [x] Use existing UserRepository.get() method (telegram_uid is the PK)
- [x] Replace `User.objects.get()` in `send_daily_horoscope.py` with UserRepository call
- [x] Replace `User.objects.get()` in `send_periodic_teaser.py` with UserRepository call
- [x] Remove `from core.models import User` imports from both files
- [x] Update tests to mock `container.core.user_repository()` instead of `core.models.User`
- [x] Verify all tests pass (261 passed)

## Investigation
Both files import `from core.models import User` and use `User.objects.get(telegram_uid=...)` directly:
- `send_daily_horoscope.py` lines 46-49: Gets User to check `last_activity` field
- `send_periodic_teaser.py` lines 57-62: Same pattern — gets User to check `last_activity`

Both use the pattern:
```python
user = User.objects.get(telegram_uid=telegram_uid)
if not user.last_activity or user.last_activity < activity_cutoff:
    continue
```

Need to use UserRepository instead, which returns UserEntity. Check if UserEntity includes `last_activity` field and if UserRepository has a method for this.

## Questions
_(no questions)_
