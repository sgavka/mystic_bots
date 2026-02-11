# TASK_022 — Refactor: use async repository methods instead of inline sync_to_async wrappers

**Is task investigated**: no
**Summary**: Multiple handlers create redundant inline `sync_to_async` wrappers for repository calls, even though all repositories already have async variants (`aget_by_telegram_uid`, `ahas_active_subscription`, etc.). Replace these with direct async method calls to simplify code and reduce overhead.

## Checkboxes

- [ ] 1. Replace inline wrappers in `horoscope/handlers/horoscope.py`
- [ ] 2. Replace inline wrappers in `horoscope/handlers/subscription.py`
- [ ] 3. Replace inline wrappers in `horoscope/handlers/language.py`
- [ ] 4. Verify all tests still pass

## Investigation

Not yet investigated. Needs analysis of each handler to confirm async repo methods exist for all operations used.

## Questions
None
