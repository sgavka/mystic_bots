# TASK_008 — Daily horoscope: schedule + teaser wall

## Commit ID

*(pending)*

## Summary

Set up Celery Beat to trigger daily horoscope generation for all users. Free users see a teaser (first few lines) with a subscription CTA. Subscribers see the full horoscope.

## Checkboxes

- [ ] Create `horoscope/tasks/send_daily_horoscope.py` — daily delivery task
- [ ] Configure Celery Beat schedule (e.g., 06:00 UTC daily)
- [ ] Implement teaser logic: split horoscope into teaser + full
- [ ] Create subscription CTA keyboard
- [ ] Create `horoscope/handlers/horoscope.py` — view horoscope handler
- [ ] Handle users with no profile (skip or prompt wizard)
- [ ] Test daily flow end-to-end

## Investigation

*(to be filled before implementation)*
