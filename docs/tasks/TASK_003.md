# TASK_003 — Telegram bot app: bot factory, middlewares, /start handler

## Commit ID

*(pending)*

## Summary

Create the `telegram_bot` Django app with bot factory (Aiogram dispatcher setup), middlewares (BotMiddleware, UserMiddleware, AppContextMiddleware), FSM storage (Redis), and basic /start handler.

## Checkboxes

- [ ] Create `telegram_bot/bot.py` — bot factory, dispatcher, router setup
- [ ] Create `telegram_bot/middlewares/bot.py` — BotMiddleware
- [ ] Create `telegram_bot/middlewares/user.py` — UserMiddleware, AppContextMiddleware
- [ ] Create `telegram_bot/handlers/start.py` — /start command handler
- [ ] Create `telegram_bot/states.py` — base FSM states
- [ ] Create `telegram_bot/utils/context.py` — AppContext
- [ ] Create `telegram_bot/management/commands/start_bot.py` — management command
- [ ] Verify bot starts and responds to /start

## Investigation

*(to be filled before implementation)*
