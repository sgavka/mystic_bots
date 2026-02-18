# TASK_063 - Add Italian and French languages with translations

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add Italian (it) and French (fr) languages to the bot with full translations.

## Checklist
- [ ] Add IT and FR to Language enum in horoscope/enums.py
- [ ] Add Italian and French to LANGUAGES in config/settings.py
- [ ] Update _DEFAULT_HOROSCOPE_LANGUAGES in config/settings.py
- [ ] Create locale/it/LC_MESSAGES/django.po with Italian translations
- [ ] Create locale/fr/LC_MESSAGES/django.po with French translations
- [ ] Compile .mo files
- [ ] Add tests for language mapping
- [ ] Run all tests

## Investigation
- Follow same pattern as TASK_058 (Hindi/Arabic)
- All handlers/keyboards are dynamic — only need config + enum + .po files
- Italian: code=it, native=Italiano, flag=🇮🇹
- French: code=fr, native=Français, flag=🇫🇷

## Questions
_(no questions)_
