investigate tasks started in telegram_bot.management.commands.start_bot.Command.on_startup:
- why horoscope is generated but not sent to user?
* for example one hindu horoscope was generated at 2026-02-21 01:12:06.160047 +00:00 but was not sent to user
* maybe need to start horoscope.tasks.send_daily_horoscope.send_daily_horoscope_notifications often? 6 time per hour as ex
