# PLAN

## Next step

**Step 11** — Analyze plan to create new tasks if needed

Current status: All 9 initial tasks complete. Project skeleton and core features implemented.

## Tasks

*(No pending tasks — all initial tasks complete)*

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
