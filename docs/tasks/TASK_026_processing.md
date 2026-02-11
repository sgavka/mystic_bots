**Is task investigated** — yes
**Commit ID** — (pending)
**Summary** — Replace custom dict-based translations with Django gettext (.po/.mo files)

**Checkboxes**
- [x] Configure Django i18n in settings (LOCALE_PATHS, LANGUAGES)
- [x] Create .po files for all 4 languages (en, ru, uk, de)
- [x] Compile .mo files
- [x] Refactor `t()` function to use Django's `gettext` with `translation.override()`
- [x] Keep backward-compatible `t(key, lang, **kwargs)` API
- [x] Update tests
- [x] Run tests (194 passed)

**Investigation**

Current state:
- 30 translation keys in TRANSLATIONS dict in `horoscope/translations.py`
- Custom `t(key, lang, **kwargs)` function
- 4 languages: en, ru, uk, de
- Used in 10 production files + 1 test file
- Django i18n enabled in settings but not used (locale dirs exist but empty)

Approach:
1. Use Django's `gettext()` backed by .po/.mo files
2. Map current keys to English msgid strings
3. `t()` function uses `translation.override(lang)` context manager
4. Create .po files manually with all 30 translations
5. Compile to .mo files
6. Keep LANGUAGE_NAMES, LANGUAGE_FLAGS, SUPPORTED_LANGUAGE_CODES, map_telegram_language unchanged

Files changed:
- `config/settings.py` — LOCALE_PATHS, LANGUAGES already configured
- `horoscope/translations.py` — replaced TRANSLATIONS dict with _KEY_TO_MSGID + Django gettext
- `locale/{en,ru,uk,de}/LC_MESSAGES/django.po` — created translation files with all 30 entries
- `locale/{en,ru,uk,de}/LC_MESSAGES/django.mo` — compiled message files
- `horoscope/tests/test_translations.py` — updated to use _KEY_TO_MSGID instead of TRANSLATIONS

**Questions** — none
