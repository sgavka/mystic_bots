# TASK_002 — Core app: User model, base repository, DI container

## Commit ID

*(pending)*

## Summary

Create the `core` Django app with User model, base Pydantic entity, base repository pattern, and dependency-injector container. This is the shared foundation for all bots.

## Checkboxes

- [ ] Create `core/models.py` — User model (telegram_uid as PK), Setting model
- [ ] Create `core/entities.py` — UserEntity, SettingEntity
- [ ] Create `core/base_entity.py` — BaseEntity with `from_attributes=True`
- [ ] Create `core/enums.py` — BotSlug enum
- [ ] Create `core/repositories/base.py` — BaseRepository with sync/async CRUD
- [ ] Create `core/repositories/user.py` — UserRepository
- [ ] Create `core/containers.py` — DI container setup
- [ ] Create `core/exceptions.py`
- [ ] Create and run migrations

## Investigation

*(to be filled before implementation)*
