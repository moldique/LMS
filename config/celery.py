import os
from urllib.parse import urlsplit, urlunsplit
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def _normalize_redis_url(url: str) -> str:
    """Заменяет только hostname localhost на 127.0.0.1, не трогая пароль/путь."""
    parts = urlsplit(url)
    if parts.hostname != 'localhost':
        return url

    userinfo = ""
    if parts.username:
        userinfo = parts.username
        if parts.password:
            userinfo += f":{parts.password}"
        userinfo += "@"

    netloc = f"{userinfo}127.0.0.1"
    if parts.port:
        netloc += f":{parts.port}"

    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


# Устанавливаем переменные окружения для Redis с 127.0.0.1 (для eventlet на Windows)
default_redis_url = 'redis://127.0.0.1:6379/0'
os.environ['CELERY_BROKER_URL'] = _normalize_redis_url(
    os.environ.get('CELERY_BROKER_URL', default_redis_url)
)
os.environ['CELERY_RESULT_BACKEND'] = _normalize_redis_url(
    os.environ.get('CELERY_RESULT_BACKEND', default_redis_url)
)

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