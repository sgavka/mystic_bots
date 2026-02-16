# TASK_057 - Add optional birth time to user profile

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Add birth time field to user info (optional — user can say "I don't know").
Also ensure all user info is present in LLM request for horoscope generation.

## Checklist
- [ ] Add birth_time field to UserProfile model (nullable)
- [ ] Update UserProfileEntity
- [ ] Add birth time step to wizard flow
- [ ] Handle "I don't know" response
- [ ] Update LLM prompt to include all user info (including birth time)
- [ ] Add translations for new messages
- [ ] Add tests for new wizard step
- [ ] Migration

## Investigation
_(not yet investigated)_

## Questions
_(no questions)_
