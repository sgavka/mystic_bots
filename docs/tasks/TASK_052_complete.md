# TASK_052 - Fix followup questions to work via chat messages

## Is task investigated
yes

## Commit ID
787da81

## Branch name
_(none)_

## Summary
Change followup question flow: remove the "Ask a question" button, let users simply type messages in chat after seeing their horoscope. Any text message from a subscriber becomes a followup question about their latest horoscope. Include previous Q&A history in LLM context. Add hint text to horoscope messages telling users they can ask followup questions.

## Checklist
- [x] Remove `ask_followup_keyboard()` and `ASK_FOLLOWUP` callback
- [x] Remove `ask_followup_callback` handler (the callback handler)
- [x] Remove `HoroscopeStates.WAITING_FOLLOWUP_QUESTION` FSM state
- [x] Change followup handler: instead of FSM state filter, catch any text message from subscribers who have today's horoscope
- [x] Include previous Q&A history in LLM prompt (update `FOLLOWUP_PROMPT` and `generate_followup_answer`)
- [x] Add followup hint text to horoscope messages (both /horoscope and daily sending)
- [x] Update handler registration order (followup must be last to act as catch-all)
- [x] Update tests

## Investigation

### Current flow
1. User sees horoscope with "Ask a question" inline button
2. User clicks button → callback handler sets FSM state `WAITING_FOLLOWUP_QUESTION`, stores `horoscope_id`
3. User types question → message handler (filtered by FSM state) processes it
4. LLM gets only horoscope text + single question (no history)

### New flow
1. User sees horoscope (with hint text: "You can ask questions about your horoscope by simply typing a message")
2. User types any text message → followup handler catches it
3. Handler checks: is user a subscriber? Does user have today's horoscope? If yes, treat as followup
4. LLM gets horoscope text + all previous Q&A + new question

### Key changes

**horoscope/handlers/followup.py:**
- Remove `ask_followup_callback` entirely
- Change `handle_followup_question` to not use FSM state filter — use no state filter (catch-all)
- Look up today's horoscope by user + date instead of FSM data
- Fetch previous followups via `followup_repo.aget_by_horoscope()` and pass to LLM
- Don't send followup keyboard in response

**horoscope/services/llm.py:**
- Update `FOLLOWUP_PROMPT` to include previous Q&A conversation
- Update `generate_followup_answer()` to accept `previous_followups` parameter

**horoscope/keyboards.py:**
- Remove `ask_followup_keyboard()` function and `KEYBOARD_ASK_FOLLOWUP` constant

**horoscope/callbacks.py:**
- Remove `ASK_FOLLOWUP` constant

**horoscope/states.py:**
- Remove `HoroscopeStates` class entirely (only had `WAITING_FOLLOWUP_QUESTION`)

**horoscope/handlers/horoscope.py:**
- Remove `ask_followup_keyboard` import and usage
- Add hint text after full horoscope for subscribers

**horoscope/tasks/generate_horoscope.py:**
- Add hint text when sending daily horoscope to subscribers

**horoscope/tasks/send_daily_horoscope.py:**
- Add hint text when sending daily horoscope notifications to subscribers

**telegram_bot/bot.py:**
- Move `followup_router` to LAST position (after all other routers) so it acts as catch-all

### Handler registration order concern
The followup handler will match ANY text message from a subscriber with a horoscope. It MUST be registered last so that command handlers (/horoscope, /start, etc.) and wizard state handlers take priority.

## Questions
_(no questions)_
