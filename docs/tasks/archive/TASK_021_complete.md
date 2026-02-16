# TASK_021 — Add language selection for user

**Is task investigated**: yes
**Commit ID**: 6c88345
**Summary**: Add language selection to the bot. Users choose a language after /start (before the wizard). Supported: English, Russian, Ukrainian, German. All bot messages and horoscope content are translated. A /language command allows changing language later.

## Checkboxes

- [ ] 1. Add `Language` enum and `preferred_language` field to `UserProfile` model + entity + migration
- [ ] 2. Create translations module (`horoscope/translations.py`) with all bot strings in 4 languages
- [ ] 3. Update `UserProfileRepository` — add `update_language()` method
- [ ] 4. Add `WAITING_LANGUAGE` state to `WizardStates`
- [ ] 5. Update wizard handler — add language selection as first step after /start
- [ ] 6. Add `/language` command handler to change language
- [ ] 7. Add language selection keyboard builder
- [ ] 8. Update all handlers to use translated strings
- [ ] 9. Update horoscope generation (template + LLM) to respect user language
- [ ] 10. Update Celery tasks to use translated strings
- [ ] 11. Update `subscribe_keyboard()` to accept language parameter
- [ ] 12. Add tests for language selection flow
- [ ] 13. Update existing tests to work with new language step

## Investigation

### Current state
- All bot messages are hardcoded English strings in handlers, tasks, keyboards, and services
- `User` model already has `language_code` from Telegram — can be used as default
- `UserProfile` model has NO language field
- No i18n infrastructure is in use (locale/ dirs have only `.gitkeep`)
- Horoscope template has English-only phrases; LLM prompt is English-only

### Approach: Dictionary-based translations (NOT Django gettext)

Django's `gettext` is designed for web apps with per-request locale middleware. For a Telegram bot, it's better to use a simple dictionary-based translation module where each string is looked up by key + language code. This avoids `.po`/`.mo` compilation, thread-local issues with async code, and is simpler to maintain.

### Implementation plan

#### 1. `horoscope/enums.py` — add `Language` enum
```python
class Language(models.TextChoices):
    EN = 'en', 'English'
    RU = 'ru', 'Russian'
    UK = 'uk', 'Ukrainian'
    DE = 'de', 'German'
```

#### 2. `horoscope/models.py` — add field to `UserProfile`
```python
preferred_language = models.CharField(
    max_length=5,
    choices=Language.choices,
    default=Language.EN,
)
```
Create migration.

#### 3. `horoscope/entities.py` — add field to `UserProfileEntity`
```python
preferred_language: str = 'en'
```

#### 4. `horoscope/translations.py` — new file with all translated strings
Dictionary structure: `TRANSLATIONS = { "key": { "en": "...", "ru": "...", "uk": "...", "de": "..." } }`
Helper: `def t(key: str, language: str, **kwargs) -> str`

All current hardcoded strings will be moved here.

#### 5. `horoscope/states.py` — add new state
```python
WAITING_LANGUAGE = State()  # First step in wizard
```

#### 6. `horoscope/keyboards.py` — add language keyboard
```python
def language_keyboard(current_language: str = None) -> InlineKeyboardMarkup
```
Show 4 language buttons with flag emojis. Mark current language if set.

#### 7. `horoscope/callbacks.py` — add language callbacks
```python
LANGUAGE_PREFIX = "lang_"
LANGUAGE_EN = "lang_en"
LANGUAGE_RU = "lang_ru"
LANGUAGE_UK = "lang_uk"
LANGUAGE_DE = "lang_de"
```

#### 8. `horoscope/handlers/wizard.py` — update flow
- `/start` for new users: show language selection keyboard (→ WAITING_LANGUAGE state)
- New callback handler for language selection during wizard
- After language is chosen, proceed to name step
- `/start` for returning users: show welcome back in their saved language

#### 9. `horoscope/handlers/language.py` — new handler file
- `/language` command shows language keyboard
- Callback handler updates language in DB
- Confirms change in the new language

#### 10. `horoscope/handlers/horoscope.py`, `subscription.py` — use translations
- Get user's language from profile (or default 'en')
- Use `t()` for all strings

#### 11. `horoscope/services/horoscope.py` — language-aware generation
- Template: use translated phrase dictionaries per language
- Pass language to `_generate_text()`

#### 12. `horoscope/services/llm.py` — add language to prompt
- Add "Write the horoscope in {language_name}" to the prompt
- Pass language parameter through the call chain

#### 13. `horoscope/tasks/` — all tasks use translations
- `generate_horoscope.py`: pass language to service, use translated "first horoscope ready" message
- `send_daily_horoscope.py`: look up user language for "subscribe" CTA
- `subscription_reminders.py`: use translated reminder/expired messages

#### 14. `horoscope/repositories/user_profile.py` — new methods
- `update_language(telegram_uid, language)` — update preferred language
- `aupdate_language(telegram_uid, language)` — async variant
- Update `create_profile()` to accept `preferred_language` parameter

#### 15. Telegram language_code mapping
Map Telegram's `language_code` (from UserMiddleware) to our Language enum for default selection:
- `ru` → `Language.RU`
- `uk` → `Language.UK`
- `de` → `Language.DE`
- everything else → `Language.EN`

### Files to modify
- `horoscope/enums.py` — add Language enum
- `horoscope/models.py` — add preferred_language field
- `horoscope/entities.py` — add preferred_language field
- `horoscope/states.py` — add WAITING_LANGUAGE state
- `horoscope/callbacks.py` — add language callbacks
- `horoscope/keyboards.py` — add language_keyboard, update subscribe_keyboard
- `horoscope/config.py` — language display names/flags
- `horoscope/repositories/user_profile.py` — add update_language methods
- `horoscope/handlers/wizard.py` — add language step, translate all strings
- `horoscope/handlers/horoscope.py` — translate all strings
- `horoscope/handlers/subscription.py` — translate all strings
- `horoscope/services/horoscope.py` — language-aware generation
- `horoscope/services/llm.py` — add language to prompt
- `horoscope/tasks/generate_horoscope.py` — translated first horoscope message
- `horoscope/tasks/send_daily_horoscope.py` — translated daily messages
- `horoscope/tasks/subscription_reminders.py` — translated reminder messages
- `telegram_bot/bot.py` — register language handler router

### New files
- `horoscope/translations.py` — all translated strings
- `horoscope/handlers/language.py` — /language command handler

## Questions
None
