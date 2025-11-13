from django.db import models


class Course(models.Model):
    
    name = models.CharField(max_length=120)
    preview = models.ImageField(upload_to='course/', blank=True, null=True)
    description = models.TextField()


class Lesson(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson/', blank=True, null=True)
    video_link = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
