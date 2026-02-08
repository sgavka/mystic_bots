# TASK_012 — Refactor: extract config, keyboards, callbacks per project structure

## Summary

CLAUDE.md documents horoscope/config.py, horoscope/keyboards.py, and horoscope/callbacks.py as separate files, but they don't exist. Keyboards and callbacks are inline in handlers, and config values (subscription price/duration, teaser line count) are hardcoded as module-level constants. Extract them to proper files following the documented structure.

## Checkboxes

- [ ] Create horoscope/config.py — centralize SUBSCRIPTION_PRICE_STARS, SUBSCRIPTION_DURATION_DAYS, TEASER_LINE_COUNT, and other magic numbers
- [ ] Create horoscope/keyboards.py — extract InlineKeyboardMarkup builders from handlers (subscribe button, etc.)
- [ ] Create horoscope/callbacks.py — define callback data constants/structures (e.g. "subscribe")
- [ ] Update horoscope/handlers/subscription.py — import from config.py and keyboards.py
- [ ] Update horoscope/handlers/horoscope.py — import from config.py and keyboards.py
- [ ] Update horoscope/services/horoscope.py — import TEASER_LINE_COUNT from config.py
- [ ] Extract zodiac sign calculation from service to horoscope/utils.py for reuse
- [ ] Remove duplicate close_old_connections() calls — move to middleware or utility decorator
