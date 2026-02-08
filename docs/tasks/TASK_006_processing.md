# TASK_006 — Horoscope generation service

## Commit ID

*(pending)*

## Summary

Implement the horoscope generation service. Uses AI API (or template-based fallback) to generate personalized horoscopes based on user profile (name, birth date, birth/living place).

## Checkboxes

- [x] Create `horoscope/services/horoscope.py` — HoroscopeService
- [x] Implement template-based generation (zodiac sign, random themed phrases)
- [x] Store generated horoscope in DB via HoroscopeRepository
- [x] Return full text and teaser (first 3 lines)
- [x] Idempotent: checks for existing horoscope before generating
- [ ] AI-based generation (LLM API call) — deferred, can replace generate_horoscope_text later

## Investigation

Template-based approach:
- Determine zodiac sign from date_of_birth
- Seed random with user_telegram_uid + date for deterministic daily output
- Compose horoscope from themed phrases (positive, advice, detail, closing)
- Split into full_text and teaser_text (first 3 lines + "...")
- HoroscopeService.generate_for_user() is idempotent (returns existing if found)
