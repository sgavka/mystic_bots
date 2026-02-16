**Is task investigated** — yes
**Commit ID** — 007e9dd
**Summary** — Make bot languages list configurable via config.settings and HOROSCOPE_LANGUAGES env var

**Checkboxes**
- [x] Add HOROSCOPE_LANGUAGES env var parsing to config/settings.py
- [x] Derive HOROSCOPE_LANGUAGE_NAMES, HOROSCOPE_LANGUAGE_FLAGS, HOROSCOPE_SUPPORTED_LANGUAGE_CODES
- [x] Update horoscope/messages.py to import from settings
- [x] Run tests (194 passed)

**Investigation**

Env var format: `HOROSCOPE_LANGUAGES=en:English:🇬🇧,ru:Русский:🇷🇺,uk:Українська:🇺🇦,de:Deutsch:🇩🇪`
Each entry is `code:name:flag` separated by commas.
Default value keeps the existing 4 languages.

**Questions** — none
