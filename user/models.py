from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='users/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []