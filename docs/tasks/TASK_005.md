# TASK_005 — Wizard flow: onboarding

## Commit ID

*(pending)*

## Summary

Implement the onboarding wizard using Aiogram FSM. Flow: /start → ask name → ask birth date (DD.MM.YYYY) → ask birth place → ask living place → trigger first horoscope generation → deliver result.

## Checkboxes

- [ ] Create `horoscope/states.py` — WizardStates FSM
- [ ] Create `horoscope/handlers/wizard.py` — step-by-step wizard handlers
- [ ] Create `horoscope/keyboards.py` — inline keyboards for wizard (skip, confirm, etc.)
- [ ] Create `horoscope/callbacks.py` — callback data structures
- [ ] Validate date input format
- [ ] Save UserProfile on wizard completion
- [ ] Trigger horoscope generation Celery task on completion
- [ ] Handle wizard restart / re-entry

## Investigation

*(to be filled before implementation)*
