# TASK_049 - Remove fallback to template-based horoscope generation

## Is task investigated
yes

## Commit ID
95e2310

## Branch name
_(none)_

## Summary
Refactor `horoscope.services.horoscope.HoroscopeService` to always use only LLM-based generation, removing the fallback to the old template-based method.

## Checklist
- [x] Remove template-based `generate_horoscope_text()` function and all its phrase templates (THEMES, POSITIVE_PHRASES, etc.)
- [x] Remove the try/except fallback in `_generate_text()` — let LLM errors propagate
- [x] Remove `is_configured` check (LLM must always be configured)
- [x] Update tests that reference the old template-based generation
- [x] Verify all tests pass

## Investigation
In `horoscope/services/horoscope.py`:
- Lines 23-212: Template phrase dictionaries (THEMES, POSITIVE_PHRASES, ADVICE_PHRASES, etc.)
- Lines 215-267: `generate_horoscope_text()` — deterministic template-based generator using seeded random
- Lines 324-355: `_generate_text()` method tries LLM first, catches Exception and falls back to template
- The fallback catch has comment "LLM failure is non-critical — fall back to template-based generation"

**Changes needed:**
1. Remove all phrase dictionaries and `generate_horoscope_text()` function
2. In `_generate_text()`, remove the try/except and `is_configured` check — just call LLM directly
3. Let exceptions propagate so callers know generation failed
4. Update/remove any tests that test the template-based path

## Questions
_(no questions)_
