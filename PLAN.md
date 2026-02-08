# PLAN

## Next step

**Step 7** — Start task implementation

Current status: Implementing TASK_001 — Project skeleton: Docker, Django, Aiogram, Poetry, Makefile setup.

## Tasks

- [ ] TASK_001 — Project skeleton: Docker, Django, Aiogram, Poetry, Makefile setup — `docs/tasks/TASK_001_processing.md` **[IN PROGRESS]**
- [ ] TASK_002 — Core app: User model, base repository, DI container — `docs/tasks/TASK_002.md`
- [ ] TASK_003 — Telegram bot app: bot factory, middlewares, /start handler — `docs/tasks/TASK_003.md`
- [ ] TASK_004 — Horoscope app: models (UserProfile, Horoscope, Subscription) — `docs/tasks/TASK_004.md`
- [ ] TASK_005 — Wizard flow: name → birth date → birth place → living place — `docs/tasks/TASK_005.md`
- [ ] TASK_006 — Horoscope generation service (AI/template-based) — `docs/tasks/TASK_006.md`
- [ ] TASK_007 — Celery setup: broker, worker, task queue for horoscope generation — `docs/tasks/TASK_007.md`
- [ ] TASK_008 — Daily horoscope: Celery beat schedule, teaser + subscription wall — `docs/tasks/TASK_008.md`
- [ ] TASK_009 — Subscription system: payment, access control, subscription management — `docs/tasks/TASK_009.md`

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
