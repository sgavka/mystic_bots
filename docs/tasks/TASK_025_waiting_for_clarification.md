# TASK_025 — Refactor: consistent language retrieval across handlers

**Is task investigated**: no
**Summary**: Language retrieval is inconsistent across handlers. Some use inline lookups, subscription.py has a `_get_user_language()` helper, and error messages sometimes fall back to hardcoded 'en' without checking user language. Create a shared async utility and use it everywhere.

## Checkboxes

- [ ] 1. Create shared `get_user_language()` async utility
- [ ] 2. Update horoscope.py handler
- [ ] 3. Update subscription.py handler
- [ ] 4. Update language.py handler (error fallback paths)
- [ ] 5. Verify all tests pass

## Investigation

Not yet investigated.

## Questions
None
