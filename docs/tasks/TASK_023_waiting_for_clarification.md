# TASK_023 — Improvement: add error handling to critical user paths

**Is task investigated**: no
**Summary**: Several critical paths lack error handling: profile creation in wizard final step, subscription activation after payment, and Celery task error logging. If these fail, users get no feedback.

## Checkboxes

- [ ] 1. Add try-except in wizard profile creation step (wizard.py)
- [ ] 2. Add try-except in successful_payment_handler (subscription.py)
- [ ] 3. Improve Celery task exception logging (generate_horoscope.py)
- [ ] 4. Add error translation keys to translations.py
- [ ] 5. Add tests for error paths

## Investigation

Not yet investigated. Needs analysis of existing error handling and what exceptions can realistically occur.

## Questions
None
