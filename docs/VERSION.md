# Documentation Version History

## Current Version: 1.1.0

## Changelog

### 1.1.0 (2026-02-14)

**Structure**
- Moved all template files into docs/project-template/ to separate template from project-specific files;
- PROJECT_INFO.md stays in project root as the only project-specific file.

**docs/USAGE.md** _(new)_
- Instructions for creating a new project from the template;
- Instructions for upgrading an existing project to a newer template version;
- Upgrade checklist with ordered list of files to review.

### 1.0.0 (2026-02-14)

**CLAUDE.md**
- Initial comprehensive version;
- Architecture: DDD with core/, telegram_bot/, domain_app/ structure;
- Patterns: repository, entity, DI, middleware, app_context, message_history, multi_bot;
- Rules: naming, type hints, named parameters, async operations, exception handling, logging;
- Commands: Docker-only execution via Makefile;
- Commit rules and development workflow.

**docs/MAIN.md**
- Development process workflow (10-step cycle);
- Task file structure and naming conventions (TASK_{number}_{status}.md);
- Task statuses: new, processing, complete, waiting_for_clarification;
- Commit format and types.

**docs/PLAN.md**
- Initial template with next step and tasks sections.
