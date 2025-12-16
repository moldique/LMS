from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import UserRegistrationView, UserViewSet, PaymentCreateView

router = DefaultRouter()
router.register(r'user', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Подключаем роутер для CRUD пользователей
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
]