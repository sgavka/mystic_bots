# TASK_037

**Is task investigated**: yes
**Commit ID**: 8e2494d
**Summary**: Remove horoscope.messages module, move texts directly to where they are used

## Checkboxes

- [ ] Move `translate()` and `map_telegram_language()` to `horoscope/utils.py`
- [ ] Move WIZARD_* and ERROR_PROFILE_CREATION_FAILED to handlers/wizard.py
- [ ] Move HOROSCOPE_NO_PROFILE, HOROSCOPE_NOT_READY, HOROSCOPE_GENERATING, HOROSCOPE_SUBSCRIBE_CTA to handlers/horoscope.py
- [ ] Move SUBSCRIPTION_* and ERROR_PAYMENT_FAILED to handlers/subscription.py
- [ ] Move LANGUAGE_CURRENT, LANGUAGE_CHANGED, LANGUAGE_NO_PROFILE to handlers/language.py
- [ ] Move KEYBOARD_SUBSCRIBE to keyboards.py
- [ ] Move HOROSCOPE_HEADER, HOROSCOPE_GREETING to services/horoscope.py
- [ ] Move TASK_FIRST_HOROSCOPE_READY to tasks/generate_horoscope.py
- [ ] Move TASK_EXPIRY_REMINDER, TASK_SUBSCRIPTION_EXPIRED to tasks/subscription_reminders.py
- [ ] Replace LANGUAGE_NAMES/FLAGS/SUPPORTED_LANGUAGE_CODES with direct settings imports
- [ ] Update tasks/send_daily_horoscope.py to import HOROSCOPE_SUBSCRIBE_CTA from handlers/horoscope.py
- [ ] Update tests
- [ ] Delete horoscope/messages.py
- [ ] Run tests and linter

## Investigation

### Approach
- Utility functions → horoscope/utils.py
- Settings proxies (LANGUAGE_NAMES, etc.) → use django.conf.settings directly
- Message constants → move to primary consumer module
- Shared constants (HOROSCOPE_SUBSCRIBE_CTA) → define in primary module, import from there

## Questions
None
