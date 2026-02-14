# TASK_051 - Feature: allow subscribers to ask questions about horoscope theme

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
New feature for users with subscription: save horoscope ID when sent, allow user to ask additional questions about the horoscope theme in chat, generating a personalized answer via LLM.

## Checklist
- [x] Investigate full implementation plan
- [x] Create model, entity, repository for horoscope follow-up questions
- [x] Add LLM method for follow-up question answering
- [x] Add FSM states, callbacks, keyboards
- [x] Add follow-up handler
- [x] Update horoscope handler to show "ask question" button for subscribers
- [x] Register in DI container
- [x] Create migration
- [x] Write tests

## Investigation

### Flow
1. Subscriber views horoscope via /horoscope → sees full text + "Ask a question" button
2. User taps "Ask a question" → callback triggers FSM state WAITING_FOLLOWUP_QUESTION, stores horoscope_id in FSM data
3. User sends a text question → handler retrieves horoscope from DB, sends question + horoscope context to LLM, saves Q&A to HoroscopeFollowup model, sends answer back
4. After answering, user gets "Ask another question" button (stays in same flow)
5. User can send /cancel or any command to exit the Q&A flow

### New Model: HoroscopeFollowup
- id (AutoField, PK)
- horoscope (ForeignKey → Horoscope)
- question_text (TextField)
- answer_text (TextField)
- model (CharField, max_length=256) — LLM model used
- input_tokens (PositiveIntegerField)
- output_tokens (PositiveIntegerField)
- created_at (DateTimeField, auto_now_add)

### Files to create/modify
1. **horoscope/models.py** — Add HoroscopeFollowup model
2. **horoscope/entities.py** — Add HoroscopeFollowupEntity
3. **horoscope/exceptions.py** — Add HoroscopeFollowupNotFoundException
4. **horoscope/repositories/followup.py** — HoroscopeFollowupRepository (create, get_by_horoscope)
5. **horoscope/repositories/__init__.py** — Export new repo
6. **horoscope/services/llm.py** — Add FOLLOWUP_PROMPT and generate_followup_answer() method
7. **horoscope/states.py** — Add HoroscopeStates.WAITING_FOLLOWUP_QUESTION
8. **horoscope/callbacks.py** — Add ASK_FOLLOWUP callback
9. **horoscope/keyboards.py** — Add ask_followup_keyboard() function
10. **horoscope/handlers/followup.py** — New handler for follow-up Q&A flow
11. **horoscope/handlers/horoscope.py** — Add "Ask a question" button when showing full horoscope to subscribers
12. **telegram_bot/bot.py** — Register followup router
13. **core/containers.py** — Add followup_repository to HoroscopeContainer
14. **Migration** — via make makemigrations
15. **horoscope/tests/test_followup.py** — Tests for handler, LLM service method, repository

### LLM Followup Prompt
The follow-up prompt will include the horoscope full_text as context and the user's question, asking the LLM to answer in the same mystical style and language.

## Questions
_(no questions)_
