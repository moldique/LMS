from django.conf import settings
from django.db import models


class Course(models.Model):
    
    name = models.CharField(max_length=120)
    preview = models.ImageField(upload_to='course/', blank=True, null=True)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    updated_at = models.DateTimeField(auto_now=True)
    

class Lesson(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson/', blank=True, null=True)
    video_link = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson')
    
    class Meta:
        ordering = ['-id']  # Сортировка по ID для пагинации


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions')
    
    class Meta:
        unique_together = [['user', 'course']]