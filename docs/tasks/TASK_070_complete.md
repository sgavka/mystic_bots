# TASK_070 - Refactor: extract horoscope type into enum

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Replace all raw string usages of horoscope type ('daily', 'first') with the existing HoroscopeType enum from horoscope/enums.py.

## Checklist
- [ ] Update horoscope/entities.py — change horoscope_type field type hint from str to HoroscopeType
- [ ] Update horoscope/repositories/horoscope.py — change parameter type hints from str to HoroscopeType
- [ ] Update horoscope/tasks/generate_horoscope.py — use HoroscopeType enum instead of raw strings
- [ ] Update horoscope/tasks/send_daily_horoscope.py — use HoroscopeType.DAILY instead of 'daily'
- [ ] Update horoscope/handlers/wizard.py — use HoroscopeType.FIRST instead of 'first'
- [ ] Update horoscope/services/horoscope.py — change type hints from str to HoroscopeType
- [ ] Update all test files to use HoroscopeType enum
- [ ] Run tests to verify

## Investigation
- HoroscopeType enum already exists in horoscope/enums.py with DAILY='daily' and FIRST='first'
- The enum is already used in models.py and services/horoscope.py
- Many places still use raw strings: tasks, handlers, repositories, tests
- Entity field horoscope_type is typed as `str` — should be `HoroscopeType`
- Repository parameters typed as `str` — should be `HoroscopeType`
- Since HoroscopeType extends TextChoices (str, Enum), it's backwards-compatible with str comparisons

## Questions
_(no questions)_
