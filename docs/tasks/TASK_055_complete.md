# TASK_055 - Add missing translations and UX feedback for followup questions

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Two improvements to followup question feature:
1. Add translations for "You can ask questions about your horoscope — just type your message!" and "Sorry, I couldn't generate an answer right now. Please try again later." to all language files (uk, ru, de)
2. After user sends a followup question, immediately send eyes emoji reaction to their message and show typing action for 10 seconds before generating the answer

## Checklist
- [x] Add followup hint translation to uk/ru/de .po files
- [x] Add error message translation to uk/ru/de .po files
- [x] Add eyes emoji reaction in followup handler after receiving message
- [x] Add 10-second typing action in followup handler
- [x] Compile messages
- [x] Run tests

## Investigation
- The followup hint string `"💬 You can ask questions about your horoscope — just type your message!"` is used in 3 places (horoscope handler, generate_horoscope task x2) but not in any .po files
- The error string `"😔 Sorry, I couldn't generate an answer right now. Please try again later."` from followup.py also not in .po files
- `app_context.set_reaction()` already exists — use with eyes emoji 👀
- For typing action, use `bot.send_chat_action(chat_id, ChatAction.TYPING)` from aiogram
- Typing action lasts ~5 seconds per Telegram API, so need to send it twice (or use asyncio loop)
- Best approach: send reaction + start typing, then generate answer (typing will show during LLM call), no need for artificial 10s delay — just keep typing active during generation

## Questions
_(no questions)_
