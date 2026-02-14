# TASK_046 - Exception handling and logging audit

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Audit all exception handling across the project to align with template v1.1.0 rules: no bare `except Exception` without justification comment, always use `exc_info=e` or `exc_info=True` in logging calls within exception handlers, only catch specific expected exception types. Review all `try/except` blocks and fix violations.

## Checklist
- [ ] Audit all `except Exception` catches — add justification comments or replace with specific exception types
- [ ] Audit all `logger.error/warning/exception` calls — ensure exc_info is included
- [ ] Check for bare `except:` blocks
- [ ] Fix any violations found
- [ ] Verify all tests pass after changes

## Investigation
_(to be filled during investigation)_

## Questions
_(no questions)_
