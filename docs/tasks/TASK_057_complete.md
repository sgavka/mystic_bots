# TASK_057 - Add optional birth time to user profile

## Is task investigated
yes

## Commit ID
b3aa3d3

## Branch name
_(none)_

## Summary
Add birth time field to user info (optional — user can say "I don't know").
Also ensure all user info is present in LLM request for horoscope generation.

## Checklist
- [x] Add birth_time field to UserProfile model (nullable)
- [x] Update UserProfileEntity
- [x] Add birth time step to wizard flow
- [x] Handle "I don't know" response
- [x] Update LLM prompt to include all user info (including birth time)
- [x] Add translations for new messages
- [x] Add tests for new wizard step
- [x] Migration

## Investigation
- Added TimeField(null=True, blank=True) to UserProfile model
- Added WAITING_BIRTH_TIME state between WAITING_DATE_OF_BIRTH and WAITING_PLACE_OF_BIRTH
- parse_time() supports HH:MM, HH.MM, 12-hour formats
- Skip keywords: "skip", "пропустить", "пропустити", "überspringen", "-"
- LLM prompt conditionally includes birth time line
- Profile ready message conditionally shows birth time
- Translations added for en, ru, uk, de

## Questions
_(no questions)_
