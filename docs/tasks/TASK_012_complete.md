# TASK_012 — Refactor: extract config, keyboards, callbacks per project structure

## Summary

CLAUDE.md documents horoscope/config.py, horoscope/keyboards.py, and horoscope/callbacks.py as separate files, but they don't exist. Keyboards and callbacks are inline in handlers, and config values (subscription price/duration, teaser line count) are hardcoded as module-level constants. Extract them to proper files following the documented structure.

## Checkboxes

- [x] Create horoscope/config.py — centralize SUBSCRIPTION_PRICE_STARS, SUBSCRIPTION_DURATION_DAYS, TEASER_LINE_COUNT, and other magic numbers
- [x] Create horoscope/keyboards.py — extract InlineKeyboardMarkup builders from handlers (subscribe button, etc.)
- [x] Create horoscope/callbacks.py — define callback data constants/structures (e.g. "subscribe")
- [x] Update horoscope/handlers/subscription.py — import from config.py and keyboards.py
- [x] Update horoscope/handlers/horoscope.py — import from config.py and keyboards.py
- [x] Update horoscope/services/horoscope.py — import TEASER_LINE_COUNT from config.py
- [x] Extract zodiac sign calculation from service to horoscope/utils.py for reuse
- [x] Remove duplicate close_old_connections() calls — removed from handlers (UserMiddleware already handles it)

## Investigation

### Constants to extract to horoscope/config.py
- `SUBSCRIPTION_PRICE_STARS = 100` (from handlers/subscription.py:19)
- `SUBSCRIPTION_DURATION_DAYS = 30` (from handlers/subscription.py:20)
- `TEASER_LINE_COUNT = 3` (from services/horoscope.py:69)

### Callback data to extract to horoscope/callbacks.py
- `"subscribe"` used in handlers/horoscope.py:56 and handlers/subscription.py:23

### Keyboards to extract to horoscope/keyboards.py
- Subscribe button keyboard from handlers/horoscope.py:53-58

### Zodiac sign utils
- `get_zodiac_sign()`, `ZODIAC_SIGNS` dict from services/horoscope.py — extract to horoscope/utils.py

### close_old_connections() calls
- UserMiddleware already calls it before every handler
- Handler calls in subscription.py:55-56 and wizard.py:123-124 are redundant

### Implementation plan
1. Create horoscope/config.py with constants
2. Create horoscope/callbacks.py with callback data
3. Create horoscope/keyboards.py with keyboard builders
4. Extract zodiac sign utils to horoscope/utils.py
5. Update all importers
6. Remove redundant close_old_connections() from handlers
