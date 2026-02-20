# TASK_069 - Feature: add /subscribe command for subscription purchase

## Is task investigated
yes

## Commit ID
18b587a

## Branch name
_(none)_

## Summary
Add a /subscribe command that allows users to buy subscriptions. If the user already has an active subscription, the new one should start from the expiration date. Also add /subscribe mention in subscription reminder messages.

## Checklist
- [ ] Add /subscribe command handler in horoscope/handlers/subscription.py
- [ ] Fix activate_or_renew to extend from expiration date (not from now) when renewing
- [ ] Show different messages for new vs renewal purchases
- [ ] Add /subscribe mention in TASK_EXPIRY_REMINDER and TASK_SUBSCRIPTION_EXPIRED messages
- [ ] Add translations for new messages
- [ ] Add tests for /subscribe command
- [ ] Update existing tests for activate_or_renew behavior change
- [ ] Run tests

## Investigation

### Current state
- Subscribe is currently only available via inline keyboard button (SubscribeCallback) shown in /horoscope teaser and expiry reminders
- No /subscribe command exists
- `activate_or_renew` in repository extends from NOW, not from expiration date — needs fix

### Implementation plan

1. **horoscope/handlers/subscription.py**: Add `/subscribe` command handler
   - Check if user has a profile (redirect to /start if not)
   - Check if user already has active subscription → show expiration date and offer to renew
   - If no subscription → show subscription offer and send invoice
   - Reuse existing SUBSCRIPTION_OFFER and invoice logic

2. **horoscope/repositories/subscription.py**: Fix `activate_or_renew`
   - When renewing an active subscription, extend from `sub.expires_at` instead of `timezone.now()`
   - Keep `timezone.now()` for creating new subscriptions

3. **horoscope/tasks/subscription_reminders.py**: Add /subscribe mention
   - Add "Use /subscribe to renew" text to TASK_EXPIRY_REMINDER
   - Add "Use /subscribe to subscribe again" text to TASK_SUBSCRIPTION_EXPIRED

4. **locale/**: Update translations for new/changed messages

5. **Tests**: Add tests for the new /subscribe command and updated renew behavior

## Questions
_(no questions)_
