# TASK_007 — Celery setup

## Commit ID

*(pending)*

## Summary

Set up Celery with Redis broker. Configure worker and beat services in Docker. Create tasks for horoscope generation queue processing.

## Checkboxes

- [ ] Create `config/celery.py` — Celery app with Redis broker
- [ ] Create `horoscope/tasks/generate_horoscope.py` — generation task
- [ ] Add Celery worker service to `docker-compose.yml`
- [ ] Add Celery beat service to `docker-compose.yml`
- [ ] Add `make celery-worker` and `make celery-beat` commands
- [ ] Verify task execution end-to-end
- [ ] Ensure tasks are idempotent

## Investigation

*(to be filled before implementation)*
