**Is task investigated** — yes
**Commit ID** —
**Summary** — Fix horoscope generation: translate header in LLM prompt, teaser shows content (not header), subscription-based sending, subscribe link in teaser

**Checkboxes**
- [ ] Fix LLM prompt to translate header/greeting
- [ ] Fix teaser generation to skip header/greeting and use actual horoscope content
- [ ] Update `_send_daily_horoscope` to check subscription and send full text or teaser
- [ ] Add subscribe link/CTA to teaser in daily send
- [ ] Update tests
- [ ] Run tests

**Investigation**

Requirements:
1. Header "Horoscope for Cancer — February 11, 2026 Dear serhiy," must be translated
   - Template-generated: already translated via `t()` function
   - LLM-generated: prompt tells LLM to write in target language, but header example is in English
   - Fix: update LLM prompt to instruct header translation
2. Teaser must NOT include header/greeting, instead include short part of horoscope content
   - Current: `lines[:TEASER_LINE_COUNT]` = header + greeting + empty line → useless
   - Fix: build teaser from content lines only (skip header, greeting, empty lines at start)
3. Send teaser if not subscribed, full text if subscribed
   - Update `_send_daily_horoscope` to check subscription via container
4. In teaser add subscribe command link
   - Append `horoscope.subscribe_cta` translation to teaser text

Files to change:
- `horoscope/services/horoscope.py` — fix teaser generation in `generate_horoscope_text`
- `horoscope/services/llm.py` — update prompt for header translation, fix teaser extraction
- `horoscope/tasks/generate_horoscope.py` — `_send_daily_horoscope` checks subscription
- `horoscope/config.py` — adjust TEASER_LINE_COUNT if needed

**Questions** — none
