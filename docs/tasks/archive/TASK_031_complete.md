**Is task investigated** — yes
**Commit ID** — bcb2f0a
**Summary** — Remove custom db_table from horoscope models, use Django-generated default table names

**Checkboxes**
- [x] Remove `db_table` and `managed = True` from all 3 model Meta classes
- [x] Create migration that renames tables from custom to Django defaults
- [x] Run tests to verify

**Investigation**

Current custom table names → Django defaults (app_label = horoscope):
- `user_profiles` → `horoscope_userprofile`
- `horoscopes` → `horoscope_horoscope`
- `subscriptions` → `horoscope_subscription`

Approach:
1. Remove `db_table` and `managed = True` from Meta classes in `horoscope/models.py`
2. Run `make makemigrations` to auto-generate migration
3. The auto-generated migration will use `AlterModelTable` operations
4. Run tests

**Questions** — none
