from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from lms.permissions import IsModeratorOrOwner
from lms.paginators import CourseLessonPagination

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