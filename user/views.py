from rest_framework import viewsets, filters, generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from user.models import Payment, User
from user.serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer
from lms.models import Course
from user.stripe_service import create_stripe_product, create_stripe_price, create_stripe_session


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
    permission_classes = [AllowAny]


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Создает платежную сессию для оплаты курса через Stripe
        """
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')
        
        if not course_id or not amount:
            return Response(
                {'error': 'Необходимо указать course_id и amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        amount_in_cents = int(float(amount) * 100)
        
        product_id = create_stripe_product(course.name, course.description)
        
        price_id = create_stripe_price(product_id, amount_in_cents)
        
        base_url = request.build_absolute_uri('/')[:-1]
        success_url = f"{base_url}/api/payments/success/"
        cancel_url = f"{base_url}/api/payments/cancel/"
        
        session_data = create_stripe_session(price_id, success_url, cancel_url)
        
        payment = Payment.objects.create(
            user=request.user,
            payment_date=datetime.now(),
            amount=amount,
            payment_method='stripe',
            paid_course=course,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data['id'],
        )
        
        return Response({
            'payment_url': session_data['url'],
            'payment_id': payment.id,
        }, status=status.HTTP_201_CREATED)
        

