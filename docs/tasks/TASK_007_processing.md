# TASK_007 — Celery setup

## Commit ID

*(pending)*

## Summary

Set up Celery with Redis broker. Configure worker and beat services in Docker. Create tasks for horoscope generation queue processing.

## Checkboxes

- [x] Create `config/celery.py` — Celery app with Redis broker (already done in TASK_001)
- [x] Create `config/__init__.py` — export celery_app for autodiscovery
- [x] Create `horoscope/tasks/generate_horoscope.py` — generate_horoscope_task
- [x] Create `horoscope/tasks/__init__.py` — exports
- [x] Celery worker/beat services in docker-compose (already done in TASK_001)
- [x] Make celery-worker/celery-beat commands (already done in TASK_001)
- [x] Wire wizard to trigger first horoscope generation via Celery task
- [x] Tasks are idempotent (HoroscopeService checks for existing before generating)

## Investigation

Celery was already configured in TASK_001. This task adds the actual task function.
- generate_horoscope_task: accepts telegram_uid, target_date (ISO string), horoscope_type
- Uses HoroscopeService.generate_for_user() which is idempotent
- Wizard flow now triggers generate_horoscope_task.delay() on profile completion
