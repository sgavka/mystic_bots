# TASK_074 - Improvement: two-phase teaser sending (daily then periodic)

## Is task investigated
yes

## Commit ID
ae38a13

## Branch name
_(none)_

## Summary
Change send_periodic_teaser_notifications to use a two-phase approach:
- First 5 days after registration: send short teaser daily
- After 5 days: send extended teaser every 5 days

## Checklist
- [ ] Update send_periodic_teaser_notifications with two-phase logic
- [ ] Add HOROSCOPE_TEASER_DAILY_DAYS setting (default 5)
- [ ] Update HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS default to 5
- [ ] Update tests
- [ ] Run tests

## Investigation

**Current behavior:** Sends teaser_text to all non-subscribers daily.

**Required behavior:**
1. Days 1-5 after profile creation: send `teaser_text` (short) daily
2. After day 5: send `extended_teaser_text` every 5 days (using `aget_last_sent_at` interval check)

**Implementation:**
1. In send_periodic_teaser_notifications, after getting profile:
   - Calculate days since `profile.created_at`
   - If <= HOROSCOPE_TEASER_DAILY_DAYS: send teaser_text
   - If > HOROSCOPE_TEASER_DAILY_DAYS: check interval via aget_last_sent_at, send extended_teaser_text
2. Add `HOROSCOPE_TEASER_DAILY_DAYS` env var (default 5)
3. Change `HOROSCOPE_PERIODIC_TEASER_INTERVAL_DAYS` default from 10 to 5

## Questions
_(no questions)_
