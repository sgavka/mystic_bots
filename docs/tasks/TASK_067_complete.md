# TASK_067 - Remove _send_daily_horoscope and overheld sending logic from generate_horoscope

## Is task investigated
yes

## Commit ID
cf6f61c

## Branch name
_(none)_

## Summary
Implement the "Recommended Approach" from TASK_066: remove `_send_daily_horoscope()` and the `send_after_generation` parameter from `generate_horoscope()`. Make `generate_horoscope()` generate-only for daily type, keeping first-horoscope sending via `_send_first_horoscope()`.

## Checklist
- [ ] Remove `_send_daily_horoscope()` function from generate_horoscope.py
- [ ] Remove `send_after_generation` parameter from `generate_horoscope()`
- [ ] Keep `_send_first_horoscope()` call for `horoscope_type='first'`
- [ ] Update on-demand /horoscope handler to generate then send inline
- [ ] Update tests for removed code
- [ ] Run tests

## Investigation

### Current callers of `generate_horoscope()`:
1. `send_daily_horoscope.py:43` — batch, `send_after_generation=False` (already correct)
2. `handlers/wizard.py:316` — first horoscope, `horoscope_type='first'` (keep sending)
3. `handlers/horoscope.py:51` — on-demand for subscribers, default params (needs change)

### Changes needed:

**generate_horoscope.py:**
- Remove `send_after_generation` param
- Remove `_send_daily_horoscope()` function entirely
- For `horoscope_type='first'`: keep `_send_first_horoscope()` call (always send)
- For `horoscope_type='daily'`: just generate, no send

**handlers/horoscope.py:**
- After `generate_horoscope()`, fetch and send the horoscope inline
- Create a small async wrapper function for asyncio.create_task()

**send_daily_horoscope.py:**
- Remove `send_after_generation=False` param (no longer needed)

## Questions
_(no questions)_
