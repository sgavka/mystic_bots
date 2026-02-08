# TASK_010 — Project standards: uv, DRY/DDD, commit rules

## Summary

Switch package manager from Poetry to uv. Add DRY and DDD principles to CLAUDE.md. Add commit message rules to PLAN.md. Remove Co-Authored-By and attribution from commit practices.

## Checkboxes

- [ ] Migrate from Poetry to uv (pyproject.toml, Dockerfile, Makefile, .gitignore)
- [ ] Remove poetry.lock, generate uv.lock
- [ ] Update CLAUDE.md: add DRY and DDD principles to architecture patterns
- [ ] Update CLAUDE.md: change "Poetry" references to "uv" throughout
- [ ] Add commit rules section to PLAN.md with format, types, and important notes
- [ ] Update CLAUDE.md Git & Commits section to match new commit rules

## Investigation

### uv migration

Current state: Poetry 2.2.1 installed in Dockerfile, pyproject.toml uses `[tool.poetry]` sections, Makefile has poetry-* targets.

Migration plan:
1. **pyproject.toml**: Remove `[tool.poetry]` section, keep `[project]` section (PEP 621), move dependencies to `[project.dependencies]` with version specifiers. Add `[dependency-groups]` for dev deps (uv convention). Remove `[build-system]` poetry backend.
2. **Dockerfile**: Replace `pip install poetry` with `pip install uv`. Replace `poetry install --no-root --no-cache` with `uv sync --frozen --no-dev` (or `uv sync --frozen` for dev). Copy `uv.lock` instead of `poetry.lock`.
3. **Makefile**: Replace `poetry-*` targets with `uv-*` targets (uv-install, uv-add, uv-update, uv-lock).
4. **Lock file**: Delete `poetry.lock`, generate `uv.lock` via Docker.

### DRY / DDD

Add to CLAUDE.md Architecture Patterns:
- **DRY (Don't Repeat Yourself)** — no code duplication; extract shared logic into services/utils
- **DDD (Domain-Driven Design)** — organize code by domain (horoscope, core, telegram_bot), keep domain logic in services, use entities as value objects

### Commit rules

Add to PLAN.md a "Commit Rules" section with:
- Format: `type: [short description]\n\n- Detail 1;\n- Detail 2;`
- Types: feat, improvement, fix, refactor, docs, test, chore
- Important: No "Generated with Claude Code" attribution, no Co-Authored-By lines
