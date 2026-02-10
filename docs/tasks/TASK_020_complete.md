## Commit ID

2b77fff

## Summary

After first horoscope is generated (via Celery task after user completes wizard), send it to the user.

## Checkboxes

- [x] Modify `generate_horoscope_task` to send the first horoscope to the user after generation
- [x] Send full text for the first horoscope (new user gift — no teaser)
- [x] Tests pass

## Investigation

### Current flow

1. Wizard completes in `horoscope/handlers/wizard.py:process_place_of_living()`:
   - Creates user profile
   - Sends "Generating your first horoscope... Please wait a moment."
   - Queues `generate_horoscope_task.delay(telegram_uid, target_date, horoscope_type='first')`

2. `horoscope/tasks/generate_horoscope.py:generate_horoscope_task()`:
   - Calls `HoroscopeService.generate_for_user()` which creates the horoscope in DB
   - Returns the horoscope ID but **never sends it to the user**

3. The daily `send_daily_horoscope_notifications_task()` only runs on schedule for daily horoscopes.

### Problem

The first horoscope is generated but never delivered to the user.

### Solution

Modify `generate_horoscope_task` to detect `horoscope_type='first'` and send the generated horoscope text directly to the user after successful generation.

- Reuse the existing pattern from `send_daily_horoscope.py:_send_messages_sync()` — create a Bot instance and send message
- Send the **full text** (not teaser) for the first horoscope — it's the user's introduction to the service
- Add a small intro message before the horoscope text

### Files to modify

- `horoscope/tasks/generate_horoscope.py` — add sending logic after first horoscope generation
