# TASK_053 - Add /refund admin command

## Is task investigated
yes

## Commit ID
b8230c7

## Branch name
_(none)_

## Summary
Add admin-only /refund command that refunds Telegram Star payments by transaction ID. No DB changes needed — just call Telegram's refund API.

## Checklist
- [x] Create admin handler with /refund command
- [x] Register admin router in bot.py
- [x] Add tests
- [x] Verify all tests pass

## Investigation

### Command format
`/refund <telegram_payment_charge_id>`

### Implementation
- Create `horoscope/handlers/admin.py` with the /refund handler
- Check `user.telegram_uid in settings.ADMIN_USERS_IDS`
- Look up subscription by `telegram_payment_charge_id` from the repo (need new repo method)
- Call `bot.refund_star_payment(user_id=subscription.user_telegram_uid, telegram_payment_charge_id=charge_id)`
- No DB changes per task requirements
- Register in `telegram_bot/bot.py` before followup router

### Key files to modify
- `horoscope/handlers/admin.py` (new)
- `horoscope/repositories/subscription.py` — add `get_by_charge_id` / `aget_by_charge_id`
- `telegram_bot/bot.py` — register admin router
- `horoscope/tests/test_admin.py` (new)

## Questions
_(no questions)_
