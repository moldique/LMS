from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from lms.permissions import IsModeratorOrOwner
from lms.paginators import CourseLessonPagination
from lms.tasks import send_course_update_email
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsModeratorOrOwner]
    pagination_class = CourseLessonPagination


    def get_queryset(self):
        
        if self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        
        return Course.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        course = serializer.save()
        subscriptions = Subscription.objects.filter(course=course)
        
        for subscription in subscriptions:
            send_course_update_email.delay(course.id, subscription.user.id)


class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]
    pagination_class = CourseLessonPagination
    
    def get_queryset(self):
        
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        
        return Lesson.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)
    
    def perform_update(self, serializer):
        lesson = serializer.save()
        course = lesson.course
        threshold = timezone.now() - timedelta(hours=4)
        was_updated = Course.objects.filter(
            id=course.id,
            updated_at__lt=threshold,
        ).update(updated_at=timezone.now())
        
        if was_updated:
            subscriptions = Subscription.objects.filter(course=course)

            for subscription in subscriptions:
                send_course_update_email.delay(course.id, subscription.user.id)


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        user = request.user
        try:
            course_item = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Курс не найден"}, status=404)
        
        with transaction.atomic():
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                course=course_item,
            )

            if created:
                message = 'подписка добавлена'
            else:
                subscription.delete()
                message = 'подписка удалена'
        
        return Response({"message": message})