import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_management.settings')

app = Celery('gym_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-weekly-payment-reminders': {
        'task': 'members.tasks.send_weekly_payment_reminders',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Every Monday at 9 AM
    },
    'send-membership-expiry-reminders': {
        'task': 'members.tasks.send_membership_expiry_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}

app.conf.timezone = 'UTC' 