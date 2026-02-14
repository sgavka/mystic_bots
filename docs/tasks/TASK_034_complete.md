**Is task investigated** — yes
**Commit ID** — b7981e4
**Summary** — Remove horoscope.translations, use Django gettext_lazy message constants

**Checkboxes**
- [x] Create horoscope/messages.py with gettext_lazy constants and translate() helper
- [x] Move language utils (LANGUAGE_NAMES, LANGUAGE_FLAGS, etc.) to messages.py
- [x] Update all 9 production files to use message constants
- [x] Delete horoscope/translations.py
- [x] Update tests
- [x] Run tests (194 passed)

**Investigation**

Replaced custom `t(key, lang)` key-based translation wrapper with standard Django gettext approach:
- All translatable strings defined as `gettext_lazy()` constants in `horoscope/messages.py`
- `translate(msg, lang, **kwargs)` helper uses `translation.override()` + `gettext()` + `format()`
- No more `_KEY_TO_MSGID` indirection layer
- 28 callsites across 9 files updated

**Questions** — none
