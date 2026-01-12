from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from user.models import User


@shared_task
def block_inactive_users():
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
       last_login__lt=month_ago
   ) | User.objects.filter(last_login__isnull=True)
    inactive_users.update(is_active=False)