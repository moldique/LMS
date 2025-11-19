from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.filters import OrderingFilter
from user.models import Payment
from user.serializers import PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, OrderingFilter]
    search_fields = ['paid_course__id', 'paid_lesson__id', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    
