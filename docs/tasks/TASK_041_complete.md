**Is task investigated** — yes
**Commit ID** —
**Summary** — Add message history tracking (model, entity, repository, middleware integration)

## Checkboxes

- [x] Create MessageHistory model in telegram_bot/models.py
- [x] Create MessageHistoryEntity in telegram_bot/entities.py
- [x] Create MessageHistoryNotFoundException in telegram_bot/exceptions.py
- [x] Create MessageHistoryRepository in telegram_bot/repositories/message_history.py
- [x] Register in DI container (core/containers.py)
- [x] Integrate into UserMiddleware to log every message/callback
- [x] Create migration
- [x] Add tests
- [x] Run tests and linter
