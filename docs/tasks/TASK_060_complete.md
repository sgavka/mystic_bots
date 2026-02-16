# TASK_060 - Add admin handler for stats

## Is task investigated
yes

## Commit ID
f66abaa

## Branch name
_(none)_

## Summary
Add /stats admin command to get usage statistics: new users, horoscopes, subscriptions — total and daily.

## Checklist
- [x] Add count() to BaseRepository
- [x] Add count_created_since() to UserProfile, Subscription, Horoscope repositories
- [x] Add count_active() to SubscriptionRepository
- [x] Add /stats command handler
- [x] Add tests
- [x] Verify all 323 tests pass

## Implementation
- Added `count()` / `acount()` to BaseRepository for total counts
- Added `count_created_since(date)` / `acount_created_since(date)` to UserProfileRepository, SubscriptionRepository, HoroscopeRepository for daily counts
- Added `count_active()` / `acount_active()` to SubscriptionRepository
- Added `/stats` command handler in admin.py that gathers all stats via `sync_to_async` and displays formatted text with total and daily sections
- Added tests: non-admin ignored, stats data displayed correctly
