# TASK_072 - Improvement: optimize get_telegram_uids_by_notification_hour query

## Is task investigated
yes (implemented)

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
The `get_telegram_uids_by_notification_hour()` method in `horoscope/repositories/user_profile.py` loads ALL user profiles without an explicit notification hour into memory, then iterates each one to check their language default. This is an N+1/full-scan problem that will degrade with more users.

## Checklist
- [x] Replace Python-side iteration with a single DB query using Q objects
- [x] Add tests for the optimized query

## Investigation

**Current code (lines 118-139):**
```python
no_explicit = UserProfile.objects.filter(notification_hour_utc__isnull=True)
for profile in no_explicit:  # Loads ALL profiles without explicit hour
    lang_hour = settings.HOROSCOPE_GENERATION_HOURS_UTC.get(profile.preferred_language, ...)
    if lang_hour == hour_utc:
        result.append(profile.user_telegram_uid)
```

**Proposed fix:** Build a Q filter that checks `preferred_language IN (languages where default hour == hour_utc)`:
```python
from django.db.models import Q

# Find which languages map to this hour
matching_langs = [
    lang for lang, hour in settings.HOROSCOPE_GENERATION_HOURS_UTC.items()
    if hour == hour_utc
]
# Also include languages not in the mapping if default hour matches
if settings.HOROSCOPE_DEFAULT_GENERATION_HOUR_UTC == hour_utc:
    no_explicit = UserProfile.objects.filter(
        notification_hour_utc__isnull=True,
    ).exclude(
        preferred_language__in=list(settings.HOROSCOPE_GENERATION_HOURS_UTC.keys()),
    ).values_list('user_telegram_uid', flat=True)
    result.extend(no_explicit)

# Languages with matching hour
if matching_langs:
    lang_matches = UserProfile.objects.filter(
        notification_hour_utc__isnull=True,
        preferred_language__in=matching_langs,
    ).values_list('user_telegram_uid', flat=True)
    result.extend(lang_matches)
```

This replaces O(n) Python iteration with 1-2 database queries.

## Questions
- Is this optimization worth doing now, or is the user count still small enough that it doesn't matter?
responce: do it