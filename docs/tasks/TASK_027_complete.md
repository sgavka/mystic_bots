**Is task investigated** — yes
**Commit ID** — 4e22509
**Summary** — Add `sent_at` and `failed_to_send_at` fields to Horoscope model, fill them in daily/first horoscope tasks

**Checkboxes**
- [x] Add `sent_at` and `failed_to_send_at` fields to Horoscope model
- [x] Add fields to HoroscopeEntity
- [x] Create migration
- [x] Add repository methods `mark_sent` / `mark_failed_to_send`
- [x] Update `send_daily_horoscope_notifications_task` to mark sent/failed
- [x] Update `_send_first_horoscope` to mark sent/failed
- [x] Add tests
- [x] Run tests

**Investigation**

Files to change:
- `horoscope/models.py` — add `sent_at`, `failed_to_send_at` (DateTimeField, null=True)
- `horoscope/entities.py` — add optional fields
- `horoscope/repositories/horoscope.py` — add `mark_sent()`, `mark_failed_to_send()` methods
- `horoscope/tasks/send_daily_horoscope.py` — after sending each message, mark horoscope as sent or failed
- `horoscope/tasks/generate_horoscope.py` — `_send_first_horoscope` should mark sent/failed
- Need to refactor `send_messages_batch` to return per-message results, or handle send tracking individually

**Questions** — none
