# TASK_077 - Refactor: register LLMService in DI container

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
LLMService() is instantiated fresh each time it's needed (in generate_horoscope.py and followup.py handler). This creates a new instance, re-reads settings on each call. Should be registered as a singleton in the DI container for consistency with the project's DI pattern.

## Checklist
- [ ] Register LLMService in DI container
- [ ] Update generate_horoscope.py to use DI
- [ ] Update followup handler to use DI
- [ ] Add tests

## Investigation
_(not yet investigated)_

## Questions
- Should this be a singleton or factory provider? (Singleton is preferred since settings don't change at runtime)
