# Важно: monkey_patch должен быть вызван ДО импорта Django и Celery
import eventlet
eventlet.monkey_patch()

from .celery import app as celery_app

# Алиас для Celery команды -A config
celery = celery_app

__all__ = ('celery_app', 'celery')