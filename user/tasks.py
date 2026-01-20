from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from user.models import User


@shared_task
def block_inactive_users():
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        Q(last_login__lt=month_ago) | Q(last_login__isnull=True, date_joined__lt=month_ago)
    )
    inactive_users.update(is_active=False)