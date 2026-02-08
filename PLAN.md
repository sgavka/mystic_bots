# PLAN

## Next step

**Step 7** — Start task implementation (TASK_010)

## Tasks

- [x] TASK_010 — Project standards: uv, DRY/DDD, commit rules *(in progress)*

---

## Rules: `docs/tasks/` folder

1. Folder with files for each task
2. Name format: `TASK_{number}_{status}.md`
3. Number: 001, 002, etc.
4. Status:
   - *(not present)* — task is created by operator
   - `new` — task acknowledged, added to plan
   - `processing` — task is being implemented
   - `complete` — task is done

## Task file structure

1. **Commit ID** — if task is already done
2. **Summary** — short summary of task
3. **Checkboxes** — task checkboxes (subtasks)
4. **Investigation** — result of investigation how to implement task

## Commit rules

### Format

```
type: short description

- Detailed point 1;
- Detailed point 2;
- More details as needed.
```

### Types

1. `feat` — New feature or functionality
2. `improvement` — Enhancement to existing feature
3. `fix` — Bug fix
4. `refactor` — Code refactoring without behavior change
5. `docs` — Documentation changes
6. `test` — Adding or updating tests
7. `chore` — Maintenance tasks, dependencies, configs

### IMPORTANT

1. Do NOT add "Generated with Claude Code" or similar attribution
2. Do NOT add "Co-Authored-By" lines
3. Keep the commit message clean and focused on the changes only
