# TASK_065 - Add Loki logging integration from redgifs_downloader_bot

## Is task investigated
yes

## Commit ID
e59ccdd

## Branch name
_(none)_

## Summary
Port Loki logging handler from redgifs_downloader_bot, add settings/env vars for Loki configuration.

## Checklist
- [x] Create core/loki_logger.py with LokiHandlerWrapper class
- [x] Add LOKI_* env vars to config/settings.py
- [x] Add LOGGING dict to config/settings.py
- [x] Update .env.example with Loki env vars
- [x] Run tests to verify nothing breaks

## Investigation
- Source: /home/sgavka/projects/python-projects/redgifs_downloader_bot/core/loki_logger.py
- No new packages needed (uses stdlib urllib)
- Env vars: LOKI_URL, LOKI_BEARER_TOKEN, LOKI_APPLICATION_NAME
- LOKI_ENABLED = all([LOKI_URL, LOKI_BEARER_TOKEN, LOKI_APPLICATION_NAME])
- Handler sends WARNING+ to Loki, console gets INFO+
- Graceful degradation: if env vars missing, Loki disabled silently

## Questions
_(no questions)_
