from rest_framework import viewsets, filters, generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from user.models import Payment, User
from user.serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, OrderingFilter]
    search_fields = ['paid_course__id', 'paid_lesson__id', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def perform_update(self, serializer):
        """Обработка пароля при обновлении пользователя"""
        if 'password' in serializer.validated_data:
            password = serializer.validated_data.pop('password')
            user = serializer.save()
            user.set_password(password)
            user.save()
        else:
            serializer.save()


class UserRegistrationView(generics.CreateAPIView):
    """Представление для регистрации нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Разрешаем регистрацию без авторизации
