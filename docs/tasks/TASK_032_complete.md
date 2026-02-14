**Is task investigated** — yes
**Commit ID** — f650b75
**Summary** — Move horoscope.config values to config.settings with HOROSCOPE_ prefix and env vars

**Checkboxes**
- [x] Add HOROSCOPE_* settings to config/settings.py with env var support
- [x] Update all imports to use django.conf.settings
- [x] Delete horoscope/config.py
- [x] Fix test mocks for new setting names
- [x] Run tests (194 passed)

**Investigation**

Moved 4 values from `horoscope/config.py` to `config/settings.py`:
- `SUBSCRIPTION_PRICE_STARS` → `HOROSCOPE_SUBSCRIPTION_PRICE_STARS` (env: HOROSCOPE_SUBSCRIPTION_PRICE_STARS, default: 1)
- `SUBSCRIPTION_DURATION_DAYS` → `HOROSCOPE_SUBSCRIPTION_DURATION_DAYS` (env: HOROSCOPE_SUBSCRIPTION_DURATION_DAYS, default: 90)
- `SUBSCRIPTION_REMINDER_DAYS` → `HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS` (env: HOROSCOPE_SUBSCRIPTION_REMINDER_DAYS, default: 3)
- `TEASER_LINE_COUNT` → `HOROSCOPE_TEASER_LINE_COUNT` (env: HOROSCOPE_TEASER_LINE_COUNT, default: 3)

Files changed:
- `config/settings.py` — added HOROSCOPE_* settings
- `horoscope/config.py` — deleted
- `horoscope/handlers/subscription.py` — updated imports
- `horoscope/tasks/subscription_reminders.py` — updated imports
- `horoscope/services/llm.py` — updated imports
- `horoscope/tests/test_translations.py` — added HOROSCOPE_TEASER_LINE_COUNT to mocks

**Questions** — none
