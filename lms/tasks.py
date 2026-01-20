from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from lms.models import Course
from user.models import User

@shared_task
def send_course_update_email(course_id, user_id):
    course = Course.objects.filter(id=course_id).first()
    user = User.objects.filter(id=user_id).first()

    if not course or not user:
        return
    
    send_mail(
        subject=f'Обновление курса: {course.name}',
        message=f'Курс "{course.name}" был обновлен. Ознакомьтесь с новыми материалами.',
        from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@lms.com',
        recipient_list=[user.email],
        fail_silently=False,
    )