# CLAUDE.md

<overview>
  Project name, concept, stack, and detailed structure are in PROJECT_INFO.md.
  <stack>Python 3.12+, Aiogram 3.x, Django 6.0, Pydantic 2.x, PostgreSQL 17, Redis 7, Celery, dependency-injector, Docker, uv</stack>
</overview>

<principles>
  <dry>
    Don't Repeat Yourself. Extract shared logic into base classes, utilities, or services.
    Every piece of knowledge must have a single, unambiguous representation.
  </dry>
  <ddd>
    Domain-Driven Design. Organize code around business domains:
    - core/ - Shared domain (User, authentication, DI container)
    - telegram_bot/ - Telegram infrastructure domain
    - domain_app/ - Feature-specific domain (one per feature area)
    Each domain has its own models, entities, repositories, and services.
    Business logic lives in services, NOT in handlers or repositories.
  </ddd>
</principles>

<architecture>
  <apps>
    - core/ - User model, base repositories, DI container, shared utilities
    - telegram_bot/ - Bot infrastructure, handlers, middlewares, FSM states, management commands
    - domain_app/ - Domain-specific: models, handlers, repositories, services, tests
  </apps>

<app_structure>
Each app must have:
- models.py (Django models)
- entities.py (Pydantic entities)
- repositories/ (data access layer)
- services/ (business logic, optional)
- exceptions.py (custom exceptions, optional)
- enums.py (enumerations, optional)
- handlers/ (aiogram handlers, for bot apps)
- states.py (FSM states, for bot apps)
- callbacks.py (callback data classes, for bot apps)
- keyboards.py (inline keyboard builders, for bot apps)
- tasks/ (Celery tasks, optional)
- tests/ (test suite)
</app_structure>

<project_structure>
project_root/
├── CLAUDE.md                  # Development rules and guidelines
├── PROJECT_INFO.md            # Project-specific info (concept, structure details)
├── Makefile                   # Build/dev automation (all commands go through here)
├── docker-compose.yml         # Development environment
├── docker-compose-prod.yml    # Production environment
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── pyproject.toml             # uv dependencies (PEP 621)
├── manage.py                  # Django management entry point
├── docs/
│   ├── MAIN.md                # Development process summary
│   ├── PLAN.md                # Current plan, task list, next step
│   └── tasks/                 # Individual task files (TASK_{number}_{status}.md)
├── config/                    # Django project config
│   ├── settings.py
│   ├── settings_test.py
│   ├── celery.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                      # Core app (shared logic)
│   ├── models.py
│   ├── entities.py
│   ├── enums.py
│   ├── exceptions.py
│   ├── containers.py          # DI container
│   ├── base_entity.py
│   ├── repositories/
│   └── services/
├── telegram_bot/              # Telegram bot base app
│   ├── bot.py                 # Bot factory, dispatcher setup
│   ├── models.py
│   ├── entities.py
│   ├── states.py              # FSM states
│   ├── handlers/
│   ├── middlewares/
│   │   ├── bot.py             # BotMiddleware
│   │   └── user.py            # UserMiddleware, AppContextMiddleware
│   ├── repositories/
│   ├── services/
│   ├── utils/
│   └── management/commands/
│       └── start_bot.py
├── <domain_app>/              # Domain-specific app (one per feature area)
│   ├── models.py
│   ├── entities.py
│   ├── enums.py
│   ├── config.py
│   ├── callbacks.py           # Callback data structures
│   ├── keyboards.py           # Inline keyboard builders
│   ├── states.py              # FSM states
│   ├── tasks/                 # Celery tasks
│   ├── handlers/
│   ├── repositories/
│   ├── services/
│   └── tests/
├── locale/                    # i18n translations
└── data/                      # Docker volumes (postgres, redis)
</project_structure>
</architecture>

<patterns>
  <repository_pattern>
    <description>
      All data access through repositories returning Pydantic entities (NEVER Django models directly).
      Each method MUST have both sync and async versions.
    </description>

    <naming>
      - Sync: get_by_id, create, update, filter, delete
      - Async: aget_by_id, acreate, aupdate, afilter, adelete (prefix with 'a')
    </naming>

    <implementation>
      <correct>
from asgiref.sync import sync_to_async
from django.db import close_old_connections

class UserRepository(BaseRepository[User, UserEntity]):
def get_by_id(self, telegram_uid: int) -> Optional[UserEntity]:
try:
user = User.objects.get(telegram_uid=telegram_uid)
return UserEntity.from_model(user)
except User.DoesNotExist:
return None

    @sync_to_async
    def aget_by_id(self, telegram_uid: int) -> Optional[UserEntity]:
        close_old_connections()
        return self.get_by_id(telegram_uid)
      </correct>
    </implementation>

    <usage>
      <correct>
@inject
async def handler(message: Message, user_repo: UserRepository = Provide[Container.user_repository]):
user = await user_repo.aget_by_id(message.from_user.id)  # Async method
</correct>

      <incorrect>
async def handler(message: Message):
user = User.objects.get(telegram_uid=message.from_user.id)  # Direct model access
# OR
user = user_repo.get_by_id(message.from_user.id)  # Sync method in async context
</incorrect>
</usage>
</repository_pattern>

<entity_pattern>
<description>
Every Django model has a Pydantic entity for type safety.
</description>

    <implementation>
from pydantic import BaseModel, ConfigDict

class UserEntity(BaseModel):
telegram_uid: int
username: Optional[str]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: 'User') -> 'UserEntity':
        return cls.model_validate(model)
    </implementation>
</entity_pattern>

<dependency_injection>
<description>
Dependencies MUST be injected in ONLY two places:
1. Method/function parameters (handlers, standalone functions)
2. Class __init__ (service classes)

      NEVER pass dependencies as method parameters between class methods.
      NEVER pass dependencies from one layer to another (handler to service, service to service).
    </description>

    <container>
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
user_repository = providers.Singleton(UserRepository)
</container>

    <usage_handlers>
      <correct>
@inject
async def handler(
message: Message,
user_repo: UserRepository = Provide[Container.user_repository]
):
user = await user_repo.aget_by_id(message.from_user.id)
</correct>
</usage_handlers>

    <usage_services>
      <correct>
class SomeService:
@inject
def __init__(
self,
user_repo: UserRepository = Provide[Container.user_repository]
):
self.user_repo = user_repo

    async def process(self, user_id: int):
        user = await self.user_repo.aget_by_id(user_id)
        await self._do_something(user)

    async def _do_something(self, user: UserEntity):
        # Access self.user_repo directly (don't pass as parameter)
        pass
      </correct>

      <incorrect>
class SomeService:
# WRONG: Passing repo between methods
async def process(self, user_id: int, user_repo: UserRepository):
user = await user_repo.aget_by_id(user_id)
await self._do_something(user, user_repo)  # Don't pass repo
</incorrect>
</usage_services>

    <standalone_functions>
      Standalone async functions that need repositories/services MUST use @inject.
      NEVER pass repositories/services as explicit parameters from caller.

      <correct>
@inject
async def process_data(
item_id: int,
items: list[str],
item_repo: ItemRepository = Provide[ApplicationContainer.domain_app.item_repository],
) -> None:
pass

# Call without passing dependencies:
await process_data(item_id=item.id, items=item_list)
</correct>
</standalone_functions>
</dependency_injection>

<middleware_pattern>
<description>
Aiogram 3.x middlewares auto-apply to all handlers (NO decorators needed).
</description>

    <chain>
      1. BotMiddleware - Injects bot_slug for multi-bot support
      2. UserMiddleware - Creates/updates user, injects UserEntity
      3. AppContextMiddleware - Manages message context
    </chain>
</middleware_pattern>

<service_layer>
<description>
Services orchestrate business logic, call repositories, return entities/DTOs.
NEVER access Django models directly in services.
</description>
</service_layer>

<multi_bot_pattern>
<description>
The project supports multiple bots from a single codebase via BotSlug enum.
</description>

    <implementation>
class BotSlug(str, Enum):
BOT_NAME = "bot_name"
</implementation>

    <usage>
      Each bot is started with: make manage start_bot --bot slug
      Bot-specific settings are loaded from environment variables: BOT_SLUG_TOKEN, etc.
    </usage>
</multi_bot_pattern>
</patterns>

<rules>
  <naming_conventions>
    - Models: PascalCase in models.py
    - Repositories: PascalCase + "Repository" suffix
    - Entities: PascalCase + "Entity" suffix
    - Services: PascalCase + "Service" suffix
    - Functions: snake_case
    - Constants: UPPER_SNAKE_CASE
    - Private methods: _underscore_prefix
    - Async repo methods: a + method_name (aget_by_id, acreate, aupdate, afilter, adelete)
  </naming_conventions>

<type_hints>
<requirement>
ALWAYS use type hints for ALL function/method parameters and return types.
NEVER omit type hints, even for simple functions.
</requirement>

    <correct>
async def handle_action(
user_id: int,
amount: int,
reply_to_message_id: Optional[int] = None,
) -> bool:
pass
</correct>

    <incorrect>
async def handle_action(user_id, amount, reply_to_message_id=None):  # No type hints
pass
</incorrect>
</type_hints>

<named_parameters>
<requirement>
All function/method calls with 3 or more arguments MUST use named parameters.
</requirement>

    <correct>
await create_item(
author_id=user.telegram_uid,
text=item_text,
data=parsed_data,
)
</correct>

    <incorrect>
await create_item(user.telegram_uid, item_text, parsed_data)
</incorrect>
</named_parameters>

<repository_rules>
<requirements>
- NEVER query Django models directly in handlers/services
- ALWAYS use repository methods
- Repositories MUST return Pydantic entities, NOT Django models
- Each method MUST have both sync and async versions (a* prefix)
- Async methods use @sync_to_async and call close_old_connections()
- Repository exceptions MUST be defined in the app's exceptions.py file
</requirements>
</repository_rules>

<entity_rules>
<requirements>
- Every Django model MUST have a corresponding Pydantic entity
- Entities MUST use model_config = ConfigDict(from_attributes=True)
- Entities MUST implement from_model() and from_models() class methods
</requirements>
</entity_rules>

<async_operations>
<requirements>
- All handlers MUST be async
- Use aiohttp for HTTP requests
- Use aiofiles for file operations
- In async handlers, ALWAYS use async repository methods (a* prefix)
</requirements>
</async_operations>

<handler_rules>
<middleware>
- NEVER use decorators for middleware logic
- Middlewares auto-apply to all handlers
- User injected as 'user' in handler context
</middleware>

    <structure>
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter

router = Router()

@router.message(StateFilter(SomeStates.ENTER_TEXT))
async def handle_text(message: Message, state: FSMContext, user: UserEntity):
# 1. Validate input
# 2. Call service/repository
# 3. Send response
# 4. Update state
pass
</structure>
</handler_rules>

<error_handling>
<exceptions>
- Create app-specific exceptions in exceptions.py
- Inherit from base AppException
- Use ForUserException for user-facing errors
</exceptions>
</error_handling>

  <configuration>
    <environment>
      - ALL secrets MUST be in environment variables
      - Validate required variables on startup
      - Provide sensible defaults for optional variables
      - NEVER commit .env file to version control
      - Use .env.example as template
    </environment>
  </configuration>

  <database>
    <migrations>
      - Run via: make migrate / make makemigrations
      - NEVER commit migration files without testing
    </migrations>

    <indexing>
      - Add indexes on frequently queried columns
      - Add unique constraints on natural keys
      - Add foreign keys for referential integrity
    </indexing>

    <enum_fields>
      - All CharField fields that use TextChoices enums MUST have max_length=256
    </enum_fields>
  </database>

<celery_tasks>
<requirements>
- Tasks must be idempotent
- Use Redis as broker
- Keep handlers lightweight — offload heavy processing to Celery tasks
</requirements>
</celery_tasks>

  <deployment>
    <docker>
      - docker-compose.yml for development
      - docker-compose-prod.yml for production
      - Separate containers: bot, database, redis
    </docker>
  </deployment>

<testing_requirements>
<after_implementation>
After implementing any task, ALWAYS run related tests:
- Run: make test app_name/tests/ -v
- If tests fail, fix the code before committing
</after_implementation>

    <new_code_tests>
      ALWAYS add tests for new code:
      - New handlers MUST have tests in app/tests/
      - New service methods MUST have unit tests
      - New repository methods MUST have tests
      - Follow existing test patterns (Arrange/Act/Assert)
      - Use aiogram-test-framework for bot handler tests
    </new_code_tests>
</testing_requirements>
</rules>

<commands>
  <critical_rule>
    NEVER run commands directly (python, uv, django, celery, etc.).
    ALWAYS use `make` commands which run everything inside Docker containers.
    This ensures consistent environment and proper dependency resolution.
  </critical_rule>

  <make>
make build              # Build Docker images
make start              # Start all services
make stop               # Stop all services
make restart            # Restart all services
make rebuild            # Stop, build and start
make fresh              # Fresh start (removes volumes)
make logs               # View bot logs
make logs-all           # View all service logs
  </make>

  <django>
make migrate            # Run migrations
make makemigrations     # Create migrations
make manage command     # Run any Django management command
make manage shell       # Django shell
  </django>

  <uv>
make uv-lock            # Regenerate uv.lock file
make uv-install         # Install dependencies
make uv-add             # Add new dependency
make uv-remove          # Remove dependency
  </uv>

  <database>
make psql               # Connect to PostgreSQL
  </database>

  <testing>
make test               # Run all tests
make test path/to/tests/test_file.py -v  # Run specific test file
make test-coverage      # Run with coverage
  </testing>

<code_quality>
make lint               # Check code with ruff
make format             # Format code with ruff
make type-check         # Check types with mypy
</code_quality>

  <celery>
make celery-worker      # Start Celery worker
make celery-beat        # Start Celery beat
  </celery>
</commands>

<commit_rules>
<format>
type: short description

    - Detailed point 1;
    - Detailed point 2;
    - More details as needed.
  </format>

  <types>
    1. feat: New feature or functionality
    2. improvement: Enhancement to existing feature
    3. fix: Bug fix
    4. refactor: Code refactoring without behavior change
    5. docs: Documentation changes
    6. test: Adding or updating tests
    7. chore: Maintenance tasks, dependencies, configs
  </types>

  <important>
    1. Do NOT add "Generated with Claude Code" or similar attribution
    2. Do NOT add "Co-Authored-By" lines
    3. Keep the commit message clean and focused on the changes only
  </important>
</commit_rules>

<development_workflow>
Always follow the workflow defined in docs/MAIN.md:
1. Check docs/PLAN.md for next step
2. Check docs/tasks/ for new tasks
3. Pick a task to implement
4. Create/update task file in docs/tasks/
5. Investigate and document implementation approach
6. Implement the task
7. Add tests
8. Commit
9. Mark task complete
10. Analyze plan for new tasks
    </development_workflow>

<resources>
  - Aiogram: https://docs.aiogram.dev/en/latest/
  - Django: https://docs.djangoproject.com/
  - Pydantic: https://docs.pydantic.dev/
  - dependency-injector: https://python-dependency-injector.ets-labs.org/
  - uv: https://docs.astral.sh/uv/
</resources>
