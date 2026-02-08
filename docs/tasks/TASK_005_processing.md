# TASK_005 — Wizard flow: onboarding

## Commit ID

*(pending)*

## Summary

Implement the onboarding wizard using Aiogram FSM. Flow: /start → ask name → ask birth date (DD.MM.YYYY) → ask birth place → ask living place → trigger first horoscope generation → deliver result.

## Checkboxes

- [x] Create `horoscope/states.py` — WizardStates FSM (4 states)
- [x] Create `horoscope/handlers/wizard.py` — step-by-step wizard handlers
- [x] Validate date input format (DD.MM.YYYY, past date, max 150 years)
- [x] Validate name length (2-100 chars) and city length (2-200 chars)
- [x] Save UserProfile on wizard completion
- [x] Handle re-entry (existing profile detected → welcome back message)
- [x] Register wizard router in bot.py setup_handlers
- [ ] Trigger horoscope generation Celery task on completion (TODO in code, will be done in TASK_007)
- [ ] Keyboards and callbacks deferred to TASK_008/009 (subscription CTA)

## Investigation

Flow: /start → check if profile exists → if yes: welcome back, if no: start wizard.
Wizard uses Aiogram FSM with 4 states: WAITING_NAME → WAITING_DATE_OF_BIRTH → WAITING_PLACE_OF_BIRTH → WAITING_PLACE_OF_LIVING.
Each step validates input and stores in FSM data. On completion, creates UserProfile in DB.
