# TASK_068 - Per-language UTC time for horoscope generation, user timezone/notification time settings

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add per-language default UTC hours for horoscope generation/sending, user profile fields for timezone and notification hour, commands to change these settings, and update background tasks to respect notification times.

## Checklist
- [ ] Add `timezone` and `notification_hour_utc` fields to UserProfile model + entity
- [ ] Create migration
- [ ] Add per-language default generation hours in settings (`HOROSCOPE_GENERATION_HOURS_UTC`)
- [ ] Add repository methods for updating timezone and notification hour
- [ ] Add FSM states for settings flow
- [ ] Add callback data classes for timezone/notification hour
- [ ] Add keyboard builders for timezone/notification hour
- [ ] Create `/timezone` command handler
- [ ] Create `/notification_time` command handler
- [ ] Register new handler router in bot.py
- [ ] Change scheduler interval from daily to hourly
- [ ] Update `generate_daily_for_all_users()` to check user's notification hour
- [ ] Update `send_daily_horoscope_notifications()` to check user's notification hour
- [ ] Update `send_periodic_teaser_notifications()` to check user's notification hour
- [ ] Add tests for new handlers
- [ ] Add tests for updated tasks
- [ ] Add tests for repository methods

## Investigation

### Design Decisions

**Per-language defaults + per-user override:**
- Settings: `HOROSCOPE_GENERATION_HOURS_UTC` env var, format `en:6,ru:5,uk:5,de:5,hi:1,ar:4,it:5,fr:5`
- These represent morning hours in each language's typical timezone
- UserProfile gets `notification_hour_utc` (nullable) — if set, overrides language default
- UserProfile gets `timezone` (CharField) — for display and converting local → UTC

**Scheduler change:**
- Change from 24h to 1h interval for generation/sending tasks
- Tasks check: is current UTC hour == user's effective notification hour?
- Effective hour = user's `notification_hour_utc` if set, else language default from settings

**Timezone format:** UTC offset integers (-12 to +14), stored as string "UTC+X" for display
- Simpler than IANA timezone names, sufficient for hour-based notification scheduling
- User selects from common UTC offsets via keyboard

### Files to modify
- `horoscope/models.py` — add fields
- `horoscope/entities.py` — add fields
- `horoscope/repositories/user_profile.py` — add update methods
- `config/settings.py` — add HOROSCOPE_GENERATION_HOURS_UTC + SCHEDULER_HOURLY_INTERVAL_SECONDS
- `horoscope/states.py` — add SettingsStates
- `horoscope/callbacks.py` — add TimezoneCallback, NotificationHourCallback
- `horoscope/keyboards.py` — add timezone/notification hour keyboards
- `horoscope/handlers/settings.py` — NEW: /timezone and /notification_time handlers
- `telegram_bot/bot.py` — register settings router
- `telegram_bot/management/commands/start_bot.py` — change intervals
- `horoscope/tasks/send_daily_horoscope.py` — add hour filtering
- `horoscope/tasks/send_periodic_teaser.py` — add hour filtering

## Questions
_(no questions)_
