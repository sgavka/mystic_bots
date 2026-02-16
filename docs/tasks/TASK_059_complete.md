# TASK_059 - Use button instead of text for skipping birth time in wizard

## Is task investigated
yes

## Commit ID
0dc8ffb

## Branch name
_(none)_

## Summary
Replace hardcoded skip text keywords with an inline keyboard button for skipping birth time input in the wizard. Remove all language-specific skip words.

## Checklist
- [x] Add "Skip" button to birth time step keyboard
- [x] Add callback data for skip action
- [x] Update wizard handler to handle skip button callback
- [x] Remove hardcoded skip word list from wizard
- [x] Update translations for skip button text
- [x] Update tests
- [x] Verify all tests pass

## Implementation
- Added `SkipBirthTimeCallback` in callbacks.py
- Added `skip_birth_time_keyboard()` in keyboards.py with translated "Skip" button
- Updated wizard handler: birth time prompt now sends with skip button keyboard
- Added new callback handler `skip_birth_time` that clears keyboard and proceeds
- Removed hardcoded skip word list from text handler
- Updated all 6 locale files (en, ru, uk, de, hi, ar) with new message text and button translation
- Updated tests to use `click_button("skip_birth_time")` instead of `send_message("skip")`
- All 321 tests pass
