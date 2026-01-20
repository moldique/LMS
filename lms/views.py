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
        course = serializer.save()

        if course.updated_at < timezone.now() - timedelta(hours=4):
            course.save()
        
            subscriptions = Subscription.objects.filter(course=course)

            for subscription in subscriptions:
                send_course_update_email.delay(course.id, subscription.user.id)


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        user = request.user
        
        course_item = Course.objects.get(id=course_id)
        
        subs_item = Subscription.objects.filter(user=user, course=course_item)
        
        if subs_item.exists():

            subs_item.delete()
            message = 'подписка удалена'
        else:

            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'
        
        return Response({"message": message})
