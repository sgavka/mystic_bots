"""
Celery configuration for Mystic Bots project.
"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('mystic_bots')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['horoscope'])
