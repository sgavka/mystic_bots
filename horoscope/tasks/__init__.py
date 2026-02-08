from horoscope.tasks.generate_horoscope import generate_horoscope_task
from horoscope.tasks.send_daily_horoscope import (
    generate_daily_for_all_users_task,
    send_daily_horoscope_notifications_task,
)

__all__ = [
    'generate_horoscope_task',
    'generate_daily_for_all_users_task',
    'send_daily_horoscope_notifications_task',
]
