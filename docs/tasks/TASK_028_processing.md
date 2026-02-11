**Is task investigated** — yes
**Commit ID** —
**Summary** — `generate_horoscope_task` should also send the daily horoscope (teaser part only) after generating

**Checkboxes**
- [ ] Update `generate_horoscope_task` to send teaser after generating daily horoscope
- [ ] Update tests
- [ ] Run tests

**Investigation**

Current flow:
- `generate_daily_for_all_users_task` queues `generate_horoscope_task` per user
- `send_daily_horoscope_notifications_task` runs separately to send notifications
- `generate_horoscope_task` only sends for `horoscope_type == 'first'`

Change:
- After generating a daily horoscope, also send it (teaser part) in `generate_horoscope_task`
- Use same pattern as `_send_first_horoscope` but send teaser_text instead
- Mark sent_at/failed_to_send_at

Files to change:
- `horoscope/tasks/generate_horoscope.py` — add sending for daily type
- `horoscope/tests/test_translations.py` — update tests

**Questions** — none
