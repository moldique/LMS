from rest_framework import serializers
from lms.models import Course, Lesson, Subscription
from lms.validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    video_link = serializers.URLField(validators=[validate_youtube_only])
    
    class Meta:
        model = Lesson
        fields = '__all__'
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.id')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

