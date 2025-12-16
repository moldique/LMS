from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='users/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Payment(models.Model):
    PAYMENT_METHOD = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Оплата через Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    paid_course = models.ForeignKey('lms.Course', null=True, blank=True, on_delete=models.CASCADE)
    paid_lesson = models.ForeignKey('lms.Lesson', null=True, blank=True, on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=100, null=True, blank=True)
