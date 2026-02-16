## Commit ID

f2dd74b

## Summary

Add emojis to all bot messages and instruct LLM to use emojis in generated horoscope text.

## Checkboxes

- [x] Add emojis to wizard handler messages
- [x] Add emojis to horoscope handler messages
- [x] Add emojis to subscription handler messages
- [x] Add emojis to keyboard button text
- [x] Add emojis to Celery task messages (first horoscope, daily, reminders)
- [x] Update LLM prompt to include emojis in generated text
- [x] Tests pass

## Investigation

### Files with bot messages

1. `horoscope/handlers/wizard.py` — onboarding wizard messages
2. `horoscope/handlers/horoscope.py` — view horoscope messages
3. `horoscope/handlers/subscription.py` — subscription/payment messages
4. `horoscope/keyboards.py` — inline keyboard button text
5. `horoscope/tasks/generate_horoscope.py` — first horoscope delivery
6. `horoscope/tasks/send_daily_horoscope.py` — daily horoscope delivery
7. `horoscope/tasks/subscription_reminders.py` — expiry/expired notifications
8. `horoscope/services/llm.py` — LLM prompt (instruct to use emojis)
