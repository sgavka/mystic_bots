**Is task investigated** — yes
**Commit ID** — 2c61e84
**Summary** — Trigger horoscope generation when subscriber uses /horoscope but horoscope not generated yet

**Checkboxes**
- [x] Update /horoscope handler to check subscription when horoscope not found
- [x] Trigger generate_horoscope_task for subscribers
- [x] Add "horoscope.generating" translation key
- [x] Add translations in all 4 languages (en, ru, uk, de)
- [x] Compile .mo files
- [x] Add tests for subscriber and non-subscriber cases
- [x] Run tests (195 passed)

**Investigation**

When user runs /horoscope and has an active subscription but horoscope is not generated:
- Trigger `generate_horoscope_task.delay()` to start generation
- Show "generating" message instead of "not ready"
- Non-subscribers still see the "not ready" message

**Questions** — none
