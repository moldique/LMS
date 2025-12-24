import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Устанавливаем переменные окружения для Redis с 127.0.0.1 (для eventlet на Windows)
if 'CELERY_BROKER_URL' not in os.environ:
    os.environ['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
else:
    os.environ['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL'].replace('localhost', '127.0.0.1')

if 'CELERY_RESULT_BACKEND' not in os.environ:
    os.environ['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'
else:
    os.environ['CELERY_RESULT_BACKEND'] = os.environ['CELERY_RESULT_BACKEND'].replace('localhost', '127.0.0.1')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Переопределяем настройки для использования 127.0.0.1 вместо localhost
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

app.autodiscover_tasks()

app.conf.beat_schedule = {
       'block-inactive-users': {
           'task': 'user.tasks.block_inactive_users',
           'schedule': crontab(hour=0, minute=0),
       },
       }