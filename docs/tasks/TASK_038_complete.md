**Is task investigated** — yes
**Commit ID** — de52cb3
**Summary** — Remove module-level text constants from horoscope/handlers/horoscope.py, inline _() calls directly where used

## Checkboxes

- [ ] Inline HOROSCOPE_NO_PROFILE, HOROSCOPE_NOT_READY, HOROSCOPE_GENERATING, HOROSCOPE_SUBSCRIBE_CTA in horoscope/handlers/horoscope.py
- [ ] Inline HOROSCOPE_SUBSCRIBE_CTA in horoscope/tasks/send_daily_horoscope.py (was imported from handler)
- [ ] Inline HOROSCOPE_SUBSCRIBE_CTA in horoscope/tasks/generate_horoscope.py (was imported from handler)
- [ ] Update horoscope/tests/test_translations.py to use inline _() strings instead of importing constants
- [ ] Run tests

## Investigation

Constants in horoscope/handlers/horoscope.py:
- HOROSCOPE_NO_PROFILE — used only in this file
- HOROSCOPE_NOT_READY — used only in this file
- HOROSCOPE_GENERATING — used only in this file
- HOROSCOPE_SUBSCRIBE_CTA — used in this file + imported by send_daily_horoscope.py, generate_horoscope.py, test_translations.py

Approach: inline all _() calls directly at usage site. For HOROSCOPE_SUBSCRIBE_CTA used in tasks, define inline there too.
