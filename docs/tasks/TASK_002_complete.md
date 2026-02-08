# TASK_002 — Core app: User model, base repository, DI container

## Commit ID

2e97a48

## Summary

Create the `core` Django app with User model, base Pydantic entity, base repository pattern, and dependency-injector container. This is the shared foundation for all bots.

## Checkboxes

- [x] Create `core/models.py` — User model (telegram_uid as PK), Setting model
- [x] Create `core/entities.py` — UserEntity, SettingEntity
- [x] Create `core/base_entity.py` — BaseEntity with `from_attributes=True`
- [x] Create `core/enums.py` — BotSlug (TextChoices), SettingType
- [x] Create `core/repositories/base.py` — BaseRepository with sync/async CRUD
- [x] Create `core/repositories/user.py` — UserRepository
- [x] Create `core/containers.py` — DI container setup
- [x] Create `core/exceptions.py`
- [x] Create migrations (0001_initial.py)

## Investigation

Studied casino_bots core app. Key patterns:
- **User model**: BigIntegerField as PK (telegram_uid), fields: username, first_name, last_name, language_code, is_premium. For horoscope we don't need is_fake.
- **Setting model**: CharField PK (name), JSONField value, type field for validation. Keep as-is.
- **BaseEntity**: Pydantic BaseModel with `from_attributes=True`, `from_model()`, `from_models()`, `to_model()`.
- **BaseRepository**: Generic[M, E] with get/add/update/delete/exists/all + async versions via sync_to_async. Supports soft delete via `deleted_at` field detection.
- **UserRepository**: Extends BaseRepository, adds get_or_create, update_by_pk, update_or_create + async versions.
- **BotSlug**: Django TextChoices with HOROSCOPE value. Already created in enums.py.
- **DI Container**: Singleton providers with factory functions, sub-containers for each app area.
- **Exceptions**: Simple per-model exception classes.
