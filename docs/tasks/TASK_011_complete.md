# TASK_011 — Refactor: fix repository pattern violations

## Summary

SubscriptionService and send_daily_horoscope Celery task bypass the repository layer by using Django ORM directly. Fix all direct model access to go through repositories, following DDD boundaries.

## Checkboxes

- [x] SubscriptionService.activate_subscription() — replace `Subscription.objects.get/create/save` with SubscriptionRepository methods
- [x] SubscriptionService.cancel_subscription() — replace `Subscription.objects.filter().update()` with repository method
- [x] SubscriptionService.expire_overdue_subscriptions() — replace direct ORM with repository method
- [x] send_daily_horoscope.py — replace `Horoscope.objects.get()` with HoroscopeRepository
- [x] send_daily_horoscope.py — replace `Subscription.objects.filter()` with SubscriptionRepository
- [x] send_daily_horoscope.py — replace `UserProfile.objects.all()` with UserProfileRepository
- [x] Add any missing repository methods needed by above refactoring
- [x] Remove all direct Django model imports from services and tasks (except in repositories)

## Investigation

### Files with violations

1. **horoscope/services/subscription.py** — `SubscriptionService`
   - `activate_subscription()` (L27-43): Uses `Subscription.objects.get()`, `sub.save()`, `Subscription.objects.create()` directly
   - `cancel_subscription()` (L58-61): Uses `Subscription.objects.filter().update()` directly
   - `expire_overdue_subscriptions()` (L67-74): Uses `Subscription.objects.filter().update()` directly
   - Note: `has_active_subscription()` already uses repository — good

2. **horoscope/tasks/send_daily_horoscope.py**
   - `generate_daily_for_all_users_task()` (L19): Uses `UserProfile.objects.all().values_list()`
   - `send_daily_horoscope_notifications_task()` (L45): Uses `UserProfile.objects.all()`
   - `send_daily_horoscope_notifications_task()` (L50): Uses `Horoscope.objects.get()`
   - `send_daily_horoscope_notifications_task()` (L58): Uses `Subscription.objects.filter().exists()`

### New repository methods needed

1. **SubscriptionRepository**:
   - `activate_or_renew(telegram_uid, duration_days, payment_charge_id)` → SubscriptionEntity
     Gets active sub, extends expiry or creates new one
   - `cancel_active(telegram_uid)` → bool
     Bulk updates active subs to cancelled
   - `expire_overdue()` → int
     Bulk updates expired active subs

2. **UserProfileRepository**:
   - `get_all_telegram_uids()` → list[int]
     Returns just UIDs for queuing (used by generate_daily_for_all_users_task)
   - Already has `all()` via BaseRepository — can be used for send task

3. **HoroscopeRepository**:
   - `get_by_user_and_date()` — already exists ✓

### Implementation plan

1. Add new methods to SubscriptionRepository
2. Add `get_all_telegram_uids()` to UserProfileRepository
3. Refactor SubscriptionService to use repository methods
4. Refactor send_daily_horoscope.py tasks to use repositories via DI container
5. Remove direct Django model imports from services and tasks
