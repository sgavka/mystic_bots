# TASK_078 - Fix Phase 1 reference date and unify generation logic

## Is task investigated
yes

## Commit ID
86905ec

## Branch name
_(none)_

## Summary
Change Phase 1/Phase 2 determination in `send_periodic_teaser_notifications` to use last subscription end date as reference (fallback to registration date). Apply same logic in `generate_and_send_horoscope`.

## Checklist
- [ ] Add `get_latest_by_user` / `aget_latest_by_user` to SubscriptionRepository
- [ ] Update `send_periodic_teaser_notifications` Phase 1 reference date logic
- [ ] Update `generate_and_send_horoscope` to apply Phase 1/Phase 2 for non-subscribers
- [ ] Update tests for periodic teaser
- [ ] Update tests for generate_and_send_horoscope
- [ ] Run tests

## Investigation

### Current behavior
- `send_periodic_teaser_notifications` uses `profile.created_at` as reference for Phase 1/Phase 2 determination
- `generate_and_send_horoscope` always sends `full_text` (only called for active subscribers)

### Required changes
1. **Phase 1 reference date**: Use last subscription `expires_at` (any status) as reference. If no subscription exists, use `profile.created_at`.
2. **`generate_and_send_horoscope`**: Apply Phase 1/Phase 2 logic for non-subscribers (subscribers still get full text)

### Implementation approach
1. Add `get_latest_by_user()` to `SubscriptionRepository` - returns subscription with latest `expires_at` regardless of status
2. Extract reference date logic into a helper (or inline it in both places)
3. In `send_periodic_teaser_notifications`: replace `profile.created_at` with reference date from last subscription
4. In `generate_and_send_horoscope`: check subscription status, apply Phase 1/Phase 2 for non-subscribers

## Questions
_(no questions)_
