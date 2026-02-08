# TASK_015 — Feature: Django admin interface

## Summary

No Django admin customization exists. Add admin classes for all models (User, UserProfile, Horoscope, Subscription) with search, filters, and read-only fields for operational visibility.

## Checkboxes

- [ ] Create core/admin.py — register User model with search by telegram_uid/username, list display, filters
- [ ] Create horoscope/admin.py — register UserProfile with search by name/telegram_uid, date_of_birth filter
- [ ] Register Horoscope model — list display (user, date, type), filters by date and type, readonly full_text preview
- [ ] Register Subscription model — list display (user, status, expires_at), filters by status, search by telegram_uid
- [ ] Add inline UserProfile display on User admin page
- [ ] Add inline Subscription display on UserProfile admin page (or on User page)
