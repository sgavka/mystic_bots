# TASK_011 — Refactor: fix repository pattern violations

## Summary

SubscriptionService and send_daily_horoscope Celery task bypass the repository layer by using Django ORM directly. Fix all direct model access to go through repositories, following DDD boundaries.

## Checkboxes

- [ ] SubscriptionService.activate_subscription() — replace `Subscription.objects.get/create/save` with SubscriptionRepository methods
- [ ] SubscriptionService.cancel_subscription() — replace `Subscription.objects.filter().update()` with repository method
- [ ] SubscriptionService.expire_overdue_subscriptions() — replace direct ORM with repository method
- [ ] send_daily_horoscope.py — replace `Horoscope.objects.get()` with HoroscopeRepository
- [ ] send_daily_horoscope.py — replace `Subscription.objects.filter()` with SubscriptionRepository
- [ ] send_daily_horoscope.py — replace `UserProfile.objects.all()` with UserProfileRepository
- [ ] Add any missing repository methods needed by above refactoring
- [ ] Remove all direct Django model imports from services and tasks (except in repositories)
