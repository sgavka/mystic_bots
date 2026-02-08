# TASK_009 — Subscription system

## Commit ID

*(pending)*

## Summary

Implement subscription management: payment flow (Telegram Stars or other), subscription status tracking, access control for full horoscope, subscription expiry handling.

## Checkboxes

- [x] Create `horoscope/services/subscription.py` — SubscriptionService
- [x] Create `horoscope/handlers/subscription.py` — subscription handlers
- [x] Implement payment flow (Telegram Stars via invoice API)
- [x] Track subscription status and expiry in DB
- [x] Gate full horoscope behind active subscription (in /horoscope handler + daily notifications)
- [x] Handle subscription renewal (extends existing) and creation
- [x] Expiry via expire_overdue_subscriptions() method
- [x] Register subscription router in bot.py
- [ ] Send subscription expiry reminders (deferred — can be a Celery beat task)

## Investigation

Telegram Stars payment flow:
1. User taps "Subscribe" button → callback_data="subscribe"
2. Bot sends invoice via answer_invoice() with XTR currency
3. Telegram handles payment UI → pre_checkout_query → answer(ok=True)
4. On successful_payment → SubscriptionService.activate_subscription()
5. Active subscription = full horoscope access in /horoscope and daily notifications
