# TASK_066 - Investigate overlap between generate_horoscope and send_daily_horoscope_notifications

## Is task investigated
yes

## Commit ID
b364d42

## Branch name
_(none)_

## Summary
`generate_horoscope()` already sends horoscopes immediately after generation (via `_send_daily_horoscope()`), making `send_daily_horoscope_notifications()` largely redundant for daily horoscopes. Refactor to separate generation from sending, removing the duplicate logic.

## Checklist
- [ ] Remove sending logic from `generate_horoscope()` — make it generate-only
- [ ] Keep `_send_first_horoscope()` call inside `generate_horoscope()` only for `horoscope_type='first'` (triggered on-demand, not by scheduler)
- [ ] Remove `_send_daily_horoscope()` function entirely (its logic is duplicated in `send_daily_horoscope_notifications()`)
- [ ] Update `send_daily_horoscope_notifications()` to also send teaser to non-subscribers (absorbing `send_periodic_teaser_notifications()` sending for today's horoscope)
- [ ] OR keep the 3-task structure but just remove duplicate sending from `generate_horoscope()`
- [ ] Update tests
- [ ] Verify scheduler still works correctly

## Investigation

### Current Flow (3 scheduled tasks, all at same daily interval)

**Task 1: `generate_daily_for_all_users()`** (send_daily_horoscope.py:9-55)
1. Gets all UserProfile telegram UIDs
2. For each: checks subscription, activity cutoff for non-subscribers
3. Calls `generate_horoscope()` which:
   - Generates horoscope via `HoroscopeService.agenerate_for_user()` (LLM call)
   - **Immediately sends** via `_send_daily_horoscope()`:
     - Subscribers → full_text + followup hint
     - Non-subscribers → teaser_text + subscribe link
   - Marks horoscope as sent/failed

**Task 2: `send_daily_horoscope_notifications()`** (send_daily_horoscope.py:58-114)
1. Gets all UserProfiles
2. For subscribers only: fetches today's horoscope
3. Skips if `sent_at is not None` ← **almost always True because Task 1 already sent it**
4. Sends full_text + followup hint, marks sent/failed

**Task 3: `send_periodic_teaser_notifications()`** (send_periodic_teaser.py:9-91)
1. For non-subscribers only: checks activity + interval since last teaser
2. Skips if `sent_at is not None` ← **almost always TRUE because Task 1 already sent it**
3. Sends extended_teaser_text + subscribe link, marks sent/failed

### The Problem

`_send_daily_horoscope()` inside `generate_horoscope()` does the **exact same work** as Tasks 2 and 3:
- Checks subscription status (duplicated from Task 1's check)
- Fetches user profile for language (duplicated from Tasks 2 & 3)
- Sends message with appropriate text (full/teaser based on subscription)
- Marks sent/failed (duplicated from Tasks 2 & 3)

Because `_send_daily_horoscope()` marks `sent_at`, Tasks 2 & 3 almost always skip every user (they only catch edge cases where sending failed silently without marking).

### Specific Duplications

| Logic | generate_horoscope → _send_daily | send_daily_notifications | send_periodic_teaser |
|-------|----------------------------------|--------------------------|----------------------|
| Subscription check | ✅ | ✅ | ✅ |
| Profile/language fetch | ✅ | ✅ | ✅ |
| Send full text to subscribers | ✅ | ✅ | — |
| Send teaser to non-subscribers | ✅ (teaser_text) | — | ✅ (extended_teaser_text) |
| Mark sent/failed | ✅ | ✅ | ✅ |

### Additional Issue: Non-subscribers get wrong teaser

- `_send_daily_horoscope()` sends `teaser_text` to non-subscribers
- `send_periodic_teaser_notifications()` is designed to send `extended_teaser_text`
- But since `_send_daily_horoscope()` already marks it sent, the periodic teaser task skips the user
- So non-subscribers never actually receive the `extended_teaser_text` — they get the shorter `teaser_text` instead

### Recommended Approach: Separate generation from sending

**Change `generate_horoscope()`:**
- For `horoscope_type='daily'`: only generate, do NOT send (remove `_send_daily_horoscope()` call)
- For `horoscope_type='first'`: keep sending (this is on-demand, not part of scheduler batch)

**Remove `_send_daily_horoscope()` function entirely.**

**Keep `send_daily_horoscope_notifications()` as-is** — it becomes the sole sender for subscribers.

**Keep `send_periodic_teaser_notifications()` as-is** — it becomes the sole sender for non-subscribers (with `extended_teaser_text` as designed).

This is the minimal-change, lowest-risk option that:
- Eliminates all duplication
- Fixes the bug where non-subscribers get `teaser_text` instead of `extended_teaser_text`
- Keeps clear separation: generate → send-to-subscribers → send-teasers-to-non-subscribers
- Doesn't change the scheduler configuration

## Questions
_(no questions)_
