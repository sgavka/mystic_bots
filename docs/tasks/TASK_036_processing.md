# TASK_036

**Is task investigated**: yes
**Commit ID**: —
**Summary**: Add LLM usage tracking table (1-to-1 with Horoscope) and a management command to calculate total cost

## Checkboxes

- [x] Create `LLMUsage` model (1-to-1 with Horoscope)
- [x] Create `LLMUsageEntity` Pydantic entity
- [x] Create `LLMUsageRepository` with create and query methods
- [x] Register repository in DI container
- [x] Update `LLMService.generate_horoscope_text()` to return usage data
- [x] Update `HoroscopeService` to save LLM usage after generation
- [x] Create migration
- [x] Create `calculate_llm_cost` management command
- [x] Add tests
- [x] Run linter

## Investigation

### Model: `LLMUsage`
- OneToOneField to `Horoscope` (horoscope_id)
- `model` — CharField(max_length=256), the LLM model name
- `input_tokens` — PositiveIntegerField
- `output_tokens` — PositiveIntegerField
- `created_at` — DateTimeField(auto_now_add=True)

### LLM response data
`litellm.completion()` returns response with:
- `response.model` — actual model used
- `response.usage.prompt_tokens` — input tokens
- `response.usage.completion_tokens` — output tokens

### Changes to LLMService
- Return `LLMResult` dataclass with (full_text, teaser_text, model, input_tokens, output_tokens) instead of tuple

### Changes to HoroscopeService
- After creating horoscope, if LLM was used, save LLM usage via repository

### Management command: `calculate_llm_cost`
- Query all LLMUsage records
- Group by model
- For each model, sum input/output tokens
- Display totals (tokens only — pricing is external)
- Show grand total

### Repository
- `LLMUsageRepository` with `create_usage()`, `get_by_horoscope_id()`, `get_usage_summary()` methods
- Each with async variant

## Questions
None
