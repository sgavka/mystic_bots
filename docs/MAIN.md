# MAIN - Development Process

Main file to keep summary of the developing process.

## References

- [docs/PLAN.md](PLAN.md) — current plan, task list, and next step
- [docs/tasks/](tasks/) — individual task files with details and investigation

## Development Steps

0. Look at "Next step" section in [docs/PLAN.md](PLAN.md)
1. Look at `docs/tasks/` if any new tasks appeared and add them to docs/PLAN.md (with file name status "new"; just created
   tasks will be without file status)
2. Get task to implement
   2.1. If exists in progress — take it to continue implementing
   2.2. Check tasks with status "waiting_for_clarification" if questions were asked already, if so start implementing
3. In docs/PLAN.md mark task as in progress
4. In task file first need to add all information how to implement task, investigation result
   4.1. If "Is task investigated" is "no", investigate it and fill task file
   4.1.1. Task can be without any parts filled, so need to take its text and create task file structure
   4.2. If needed, add questions to ask operator in task file and set task status to "waiting_for_clarification"
5. Clear context
6. Start task implementation
   6.1. Create new branch if needed
   6.2. Update docs/PLAN.md with next step after implementation of each task's sub-task / step
   6.3. Add tests for new or changed functionality
   6.3.1. Use package `aiogram-test-framework` for Telegram bot testing, for diferent user cases
7. Change task file name to mark it's status as "complete"
8. Add commit id in task file
   8.1. If task was asked to be implemented in separate branch, add branch name
9. Remove task from docs/PLAN.md
10. Analyze plan to create new tasks if needed

## If all tasks are "complete" or "waiting_for_clarification"

1. Look at tests coverage and add more tests to increase coverage
2. Run linter and fix all issues
3. Look at code and find possible improvements then create tasks from them with status "waiting_for_clarification"

### Important
- After completion of any of the steps, always update docs/PLAN.md with next step

## Rules: `docs/tasks/` folder

1. Folder with files for each task
2. Name format: `TASK_{number}_{status}.md`
3. Number: 001, 002, etc.
4. Status:
   - *(not present)* — task is created by operator
   - `new` — task acknowledged, added to plan
   - `processing` — task is being implemented
   - `complete` — task is done
   - `waiting_for_clarification` — task wait for clarification from operator

## Task file structure

**Is task investigated** — yes/no
**Commit ID** — if task is already done
**Branch name** — optional, if task is implemented in separate branch
**Summary** — short summary of task
**Checkboxes** — task checkboxes (subtasks)
**Investigation** — result of investigation how to implement task
**Questions** — questions to ask operator (if needed)

### Example task file

```markdown
# TASK_001 - Set up review_bot repositories

## Is task investigated
yes

## Commit ID
_(not yet completed)_

## Branch name
_(none)_

## Summary
Create repository classes for all review_bot models following the base repository pattern.

## Checklist
- [ ] Create ReviewRepository
- [ ] Create EmailContactRepository
- [ ] Create PhoneContactRepository
- [ ] Create IBANContactRepository
- [ ] Create BankCardContactRepository
- [ ] Create FullNameContactRepository
- [ ] Create ReviewMediaRepository
- [ ] Create M2M relationship repository methods

## Investigation
- Follow BaseRepository pattern from core/repositories/base.py
- Each repository needs sync + async method pairs
- M2M operations should be handled through dedicated methods

## Questions
_(no questions)_
```


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
