# TASK_054 - Migrate horoscope callbacks to aiogram CallbackData classes

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary

### Why callbacks were plain strings
The callbacks.py module used plain string constants (`SUBSCRIBE = "subscribe"`, `LANGUAGE_PREFIX = "lang_"`) because it was the simplest approach during initial development. The language callback used a manual prefix+code pattern (`f"{LANGUAGE_PREFIX}{lang_code}"`) with manual parsing (`callback.data[len(LANGUAGE_PREFIX):]`).

### Why aiogram CallbackData classes are better
1. **Type safety**: Callback data is validated via Pydantic models, preventing invalid data
2. **No manual parsing**: `callback_data.code` instead of `callback.data[len(prefix):]`
3. **Magic filter integration**: `LanguageCallback.filter()` automatically handles matching and unpacking
4. **Consistent pattern**: aiogram's recommended approach, documented and well-tested

### What was changed
- Replaced string constants with `CallbackData` subclasses:
  - `SubscribeCallback(CallbackData, prefix="subscribe")` — no fields
  - `LanguageCallback(CallbackData, prefix="lang")` — has `code: str` field
- Updated all handlers to use `.filter()` and receive `callback_data` parameter
- Updated keyboard builders to use `.pack()` instead of string formatting
- Data format changed from `lang_en` to `lang:en` (aiogram uses `:` separator)

### Suggested CLAUDE.md rule (NOT added, just noted here)
```
<callback_data_pattern>
  <requirements>
    - ALL callback data MUST use aiogram CallbackData classes (from aiogram.filters.callback_data)
    - NEVER use plain string constants for callback data
    - Define all callback data classes in the app's callbacks.py file
    - Use .pack() to serialize and .filter() to register handlers
    - Handler receiving callback data MUST declare callback_data parameter with the correct type
  </requirements>
</callback_data_pattern>
```

## Checklist
- [x] Replace string constants with CallbackData classes in callbacks.py
- [x] Update keyboards.py to use .pack()
- [x] Update subscription handler to use SubscribeCallback.filter()
- [x] Update language handler to use LanguageCallback.filter() and callback_data parameter
- [x] Update wizard handler to use LanguageCallback.filter() and callback_data parameter
- [x] Update tests for new callback data format (lang: separator)
- [x] Verify all tests pass

## Investigation
See summary above.

## Questions
_(no questions)_
