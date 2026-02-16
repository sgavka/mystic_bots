# TASK_003 — Telegram bot app: bot factory, middlewares, /start handler

## Commit ID

9b38e2a

## Summary

Create the `telegram_bot` Django app with bot factory (Aiogram dispatcher setup), middlewares (BotMiddleware, UserMiddleware, AppContextMiddleware), FSM storage (Redis), and basic /start handler.

## Checkboxes

- [x] Create `telegram_bot/bot.py` — bot factory, dispatcher, router setup
- [x] Create `telegram_bot/middlewares/bot.py` — BotMiddleware
- [x] Create `telegram_bot/middlewares/user.py` — UserMiddleware, AppContextMiddleware
- [x] Create `telegram_bot/handlers/start.py` — /start command handler
- [x] Create `telegram_bot/handlers/errors.py` — global error handler
- [x] Create `telegram_bot/states.py` — base FSM states (MainStates)
- [x] Create `telegram_bot/utils/context.py` — AppContext
- [x] Create `telegram_bot/management/commands/start_bot.py` — management command
- [ ] Verify bot starts and responds to /start (requires valid bot token)

## Investigation

Studied casino_bots telegram_bot app. Simplified for horoscope:
- Removed LoggingMiddleware and i18n middleware (can add later)
- Removed UserToBot and Payment dependencies from UserMiddleware
- Simplified AppContext (no tracked messages, no game-specific features)
- Single bot type (HOROSCOPE) — no conditional handler registration
- Error handler logs exceptions only (no Telegram error notifications yet)
