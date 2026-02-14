# TASK_050 - Fix direct User model access in Celery tasks

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Replace direct `User.objects.get()` calls in `horoscope/tasks/send_daily_horoscope.py` and `horoscope/tasks/send_periodic_teaser.py` with repository methods.

## Checklist
- [ ] Add `get_by_telegram_uid()` / `aget_by_telegram_uid()` method to UserRepository (if not exists)
- [ ] Replace `User.objects.get()` in `send_daily_horoscope.py` with UserRepository call
- [ ] Replace `User.objects.get()` in `send_periodic_teaser.py` with UserRepository call
- [ ] Remove `from core.models import User` imports from both files
- [ ] Update tests if needed
- [ ] Verify all tests pass

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
