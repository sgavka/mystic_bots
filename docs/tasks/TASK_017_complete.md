# TASK_017 — Feature: LLM-based horoscope generation

## Summary

Replace template-based horoscope generation with actual AI-powered text generation via LLM API. Keep template as fallback. Use user's zodiac sign, birth info, and current date for personalized horoscopes.

## Checkboxes

- [x] Add LLM client dependency (litellm>=1.40) to pyproject.toml
- [x] Add LLM_API_KEY, LLM_MODEL, LLM_BASE_URL, LLM_TIMEOUT to config/settings.py (env vars)
- [x] Create horoscope/services/llm.py — LLMService with generate_horoscope_text() method
- [x] Build prompt template using: zodiac sign, date of birth, place of birth, place of living, target date
- [x] Update HoroscopeService.generate_for_user() — call LLMService via _generate_text(), fallback to template on failure
- [x] Generate both full_text and teaser_text from LLM response
- [x] Add timeout for LLM API calls (LLM_TIMEOUT setting, default 30s)
- [x] Update .env.example with LLM configuration variables

## Investigation

### LLM SDK choice
- litellm — unified interface to OpenAI, Anthropic, etc. Supports LLM_BASE_URL for custom endpoints.

### Settings to add
- `LLM_API_KEY` — API key for the LLM provider
- `LLM_MODEL` — model identifier (e.g. "gpt-4o-mini", "anthropic/claude-3-haiku")
- `LLM_BASE_URL` — optional base URL override for custom/proxy endpoints

### LLMService design
- `generate_horoscope_text(zodiac_sign, name, date_of_birth, place_of_birth, place_of_living, target_date)` → (full_text, teaser_text)
- Uses litellm.completion() with timeout
- Prompt asks for a personalized horoscope with sections
- Parses response to split full_text and teaser_text

### HoroscopeService changes
- Try LLMService first
- On failure (any exception), log and fallback to template generation
- Only use LLM if LLM_API_KEY is configured
