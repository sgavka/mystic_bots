# Template Usage Guide

This document describes how to create a new project from this template and how to upgrade an existing project to a newer template version.

## Template Structure

All template files are located in `docs/project-template/`. This directory mirrors the target project root structure:

```
docs/project-template/
├── CLAUDE.md                  # Development rules and guidelines
├── Makefile                   # Build/dev automation
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # Project readme template
├── docker-compose.yml         # Development environment
├── docker-compose-prod.yml    # Production environment
├── docker/                    # Dockerfile & entrypoint
├── core/                      # Core app (base entity, base repository)
├── telegram_bot/              # Telegram bot infrastructure
└── docs/                      # Development workflow docs
    ├── MAIN.md                # Development process
    ├── PLAN.md                # Plan template
    ├── VERSION.md             # Version tracking
    └── tasks/                 # Task files directory
```

## Creating a New Project

1. Create a new project directory and initialize git:

```bash
mkdir my-new-project && cd my-new-project
git init
```

2. Copy all template files to the project root:

```bash
cp -r /path/to/template/docs/project-template/* .
cp /path/to/template/docs/project-template/.env.example .
cp /path/to/template/docs/project-template/.gitignore .
```

3. Create `PROJECT_INFO.md` in the project root with your project-specific info (use the template's `PROJECT_INFO.md` as a reference for the structure).

4. Update project-specific values:
   - `CLAUDE.md` — update stack versions if needed
   - `.env.example` — adjust environment variables for your project
   - `docker-compose.yml` / `docker-compose-prod.yml` — adjust service names and ports
   - `Makefile` — adjust project name if referenced
   - `README.md` — update with your project description

5. Build and start:

```bash
make build
make start
make migrate
```

## Upgrading an Existing Project

When a new template version is released, follow these steps to upgrade your project.

### Step 1: Check the Template Changelog

Read `docs/project-template/docs/VERSION.md` in the template repo to see what changed since your last upgrade.

### Step 2: Compare and Apply Changes

For each file in `docs/project-template/`, compare it with the corresponding file in your project:

```bash
# Example: compare CLAUDE.md
diff /path/to/template/docs/project-template/CLAUDE.md ./CLAUDE.md

# Example: compare a source file
diff /path/to/template/docs/project-template/core/base_entity.py ./core/base_entity.py
```

### Step 3: Apply Updates

For each changed file:

- **If the file does not exist in your project** — copy it from the template:

```bash
cp /path/to/template/docs/project-template/path/to/file ./path/to/file
```

- **If the file exists in your project** — merge the template's new logic into your existing file. Do NOT blindly overwrite, as your project may have custom modifications. Review each diff and integrate the new patterns/rules while preserving your project-specific code.

### Step 4: Create Refactoring Tasks

After applying template updates, create tasks in `docs/tasks/` for any code that needs to be refactored to follow the new template patterns. For example, if the template introduces a new middleware pattern, create a task to update your existing middlewares.

Task file format (per `docs/MAIN.md`):

```markdown
# TASK_XXX - Refactor [component] to follow updated template

## Is task investigated
no

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Update [component] to align with template version X.Y.Z changes:
- [list specific changes from template changelog]

## Checklist
- [ ] Update [file1]
- [ ] Update [file2]
- [ ] Add/update tests

## Investigation
_(to be filled during investigation)_

## Questions
_(no questions)_
```

Add these tasks to `docs/PLAN.md` and follow the standard development workflow from `docs/MAIN.md`.

### Step 5: Record the Upgrade

Note the template version you upgraded to so you can track future changes. You can add a comment in your project's `docs/PLAN.md` or create a commit message referencing the template version.

## Upgrade Checklist

When upgrading, check these files in order:

1. **CLAUDE.md** — new rules, patterns, or architecture changes
2. **Makefile** — new commands or changed targets
3. **docker-compose.yml** / **docker-compose-prod.yml** — infrastructure changes
4. **docker/Dockerfile** — base image or build changes
5. **docker/entrypoint.sh** — startup changes
6. **.env.example** — new environment variables
7. **core/base_entity.py** — base entity changes
8. **core/repositories/base.py** — base repository changes
9. **telegram_bot/** — middleware, bot setup, app_context changes
10. **docs/MAIN.md** — development workflow changes
