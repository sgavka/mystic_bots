# TASK_017 — Feature: LLM-based horoscope generation

## Summary

Replace template-based horoscope generation with actual AI-powered text generation via LLM API. Keep template as fallback. Use user's zodiac sign, birth info, and current date for personalized horoscopes.

## Checkboxes

- [ ] Add LLM client dependency (e.g. openai, litellm, or anthropic SDK) to pyproject.toml
- [ ] Add LLM_API_KEY, LLM_MODEL, LLM_BASE_URL to config/settings.py (env vars)
- [ ] Create horoscope/services/llm.py — LLMService with generate_horoscope_text() method
- [ ] Build prompt template using: zodiac sign, date of birth, place of birth, place of living, target date
- [ ] Update HoroscopeService.generate_for_user() — call LLMService, fallback to template on failure
- [ ] Generate both full_text and teaser_text from LLM response
- [ ] Add timeout and retry for LLM API calls
- [ ] Update .env.example with LLM configuration variables
