# TASK_015 — Feature: Django admin interface

## Summary

No Django admin customization exists. Add admin classes for all models (User, UserProfile, Horoscope, Subscription) with search, filters, and read-only fields for operational visibility.

## Checkboxes

- [x] Create core/admin.py — register User and Setting models with search, list display, filters
- [x] Create horoscope/admin.py — register UserProfile with search by name/telegram_uid, date_of_birth filter
- [x] Register Horoscope model — list display (user, date, type), filters by date and type, readonly full_text preview
- [x] Register Subscription model — list display (user, status, expires_at), filters by status, search by telegram_uid
- [x] ~~Add inline UserProfile display on User admin page~~ — skipped (no ForeignKey relationship, models use BigIntegerField)
- [x] ~~Add inline Subscription display on UserProfile admin page~~ — skipped (same reason)

## Investigation

### Model relationships
- UserProfile.user_telegram_uid is a BigIntegerField (not ForeignKey to User)
- Subscription.user_telegram_uid is a BigIntegerField (not ForeignKey)
- Django admin inlines require ForeignKey relationships — inlines skipped
- All models registered with appropriate search/filter/readonly fields instead
