# TASK_058 - Add Hindi and Arabic languages

## Is task investigated
yes

## Commit ID
e72b3c3

## Branch name
_(none)_

## Summary
Add Hindi and Arabic language support. Ensure all texts are translated.

## Checklist
- [x] Add Hindi (hi) and Arabic (ar) to supported languages
- [x] Create locale files for Hindi
- [x] Create locale files for Arabic
- [x] Translate all existing message strings
- [x] Update language selection keyboard (auto from settings)
- [x] Add tests for new languages
- [x] Verify all texts are covered
- [x] Add Hindi/Arabic skip words to birth time wizard step

## Investigation
- Added HI/AR to Language enum in horoscope/enums.py
- Added hi/ar to LANGUAGES in config/settings.py
- Added hi/ar to _DEFAULT_HOROSCOPE_LANGUAGES with native names and flags
- Created locale/hi/LC_MESSAGES/django.po with full Hindi translations
- Created locale/ar/LC_MESSAGES/django.po with full Arabic translations
- Compiled .mo files
- Added skip words (छोड़ें, تخطي) for birth time wizard step
- Added Hindi/Arabic tests to TestTranslationFunction and TestMapTelegramLanguage
- Added birth time constants to _ALL_MESSAGE_CONSTANTS for completeness check
- All 321 tests pass
