from rest_framework import viewsets, filters, generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from decimal import Decimal, InvalidOperation

from user.models import Payment, User
from user.serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer
from lms.models import Course
from user.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
    cleanup_stripe_resources,
    StripeServiceError,
)


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
        
        try:
            amount_decimal = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            return Response(
                {'error': 'Некорректное значение amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount_decimal <= 0:
            return Response(
                {'error': 'amount должен быть положительным числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount_in_cents = int(amount_decimal * 100)
        
        product_id = None
        price_id = None
        session_id = None

        try:
            product_id = create_stripe_product(course.name, course.description)
            price_id = create_stripe_price(product_id, amount_in_cents)

            base_url = request.build_absolute_uri('/')[:-1]
            success_url = f"{base_url}/api/users/payments/success/"
            cancel_url = f"{base_url}/api/users/payments/cancel/"

            session_data = create_stripe_session(price_id, success_url, cancel_url)
            session_id = session_data['id']

            with transaction.atomic():
                payment = Payment.objects.create(
                    user=request.user,
                    payment_date=timezone.now(),
                    amount=amount_decimal,
                    payment_method='stripe',
                    paid_course=course,
                    stripe_product_id=product_id,
                    stripe_price_id=price_id,
                    stripe_session_id=session_id,
                )
        except StripeServiceError as exc:
            cleanup_stripe_resources(
                product_id=product_id,
                price_id=price_id,
                session_id=session_id,
            )
            return Response(
                {'error': str(exc)},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception:
            cleanup_stripe_resources(
                product_id=product_id,
                price_id=price_id,
                session_id=session_id,
            )
            return Response(
                {'error': 'Не удалось создать платеж. Попробуйте позже.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'payment_url': session_data['url'],
            'payment_id': payment.id,
        }, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'success'})


class PaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'cancel'})
        
