from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from django.urls import reverse
from user.models import User
from lms.models import Course, Lesson, Subscription


class LessonCRUDTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание пользователей
        self.user_owner = User.objects.create_user(
            email='owner@test.com',
            username='owner',
            password='testpass123'
        )
        
        self.user_other = User.objects.create_user(
            email='other@test.com',
            username='other',
            password='testpass123'
        )
        
        # Создание группы модераторов
        self.moderator_group = Group.objects.create(name='moderators')
        
        # Создание пользователя-модератора
        self.user_moderator = User.objects.create_user(
            email='moderator@test.com',
            username='moderator',
            password='testpass123'
        )
        self.user_moderator.groups.add(self.moderator_group)
        
        # Создание курсов
        self.course_owner = Course.objects.create(
            name='Курс владельца',
            description='Описание курса владельца',
            owner=self.user_owner
        )
        
        # Создание уроков
        self.lesson_owner = Lesson.objects.create(
            name='Урок владельца',
            description='Описание урока владельца',
            video_link='https://www.youtube.com/watch?v=test1',
            course=self.course_owner,
            owner=self.user_owner
        )
    
    def test_create_lesson_by_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)
        
        url = reverse('lesson-list-create')
        data = {
            'name': 'Новый урок',
            'description': 'Описание нового урока',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course_owner.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.get(name='Новый урок').owner, self.user_owner)
    
    def test_create_lesson_by_moderator_forbidden(self):
        """Тест создания урока модератором (должен быть запрещен)"""
        self.client.force_authenticate(user=self.user_moderator)
        
        url = reverse('lesson-list-create')
        data = {
            'name': 'Урок модератора',
            'description': 'Описание урока модератора',
            'video_link': 'https://www.youtube.com/watch?v=mod',
            'course': self.course_owner.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_lessons_by_owner(self):
        """Тест получения списка уроков владельцем (видит только свои)"""
        self.client.force_authenticate(user=self.user_owner)
        
        url = reverse('lesson-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем формат ответа пагинации
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)
    
    def test_update_own_lesson(self):
        """Тест обновления своего урока"""
        self.client.force_authenticate(user=self.user_owner)
        
        url = reverse('lesson-detail', kwargs={'pk': self.lesson_owner.id})
        data = {
            'name': 'Обновленный урок',
            'description': 'Обновленное описание',
            'video_link': 'https://www.youtube.com/watch?v=updated',
            'course': self.course_owner.id
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson_owner.refresh_from_db()
        self.assertEqual(self.lesson_owner.name, 'Обновленный урок')
    
    def test_delete_own_lesson(self):
        """Тест удаления своего урока"""
        self.client.force_authenticate(user=self.user_owner)
        
        url = reverse('lesson-detail', kwargs={'pk': self.lesson_owner.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)


class SubscriptionTestCase(APITestCase):
    """Тесты для функционала подписки на курсы"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='testpass123'
        )
        
        self.user_other = User.objects.create_user(
            email='other@test.com',
            username='other',
            password='testpass123'
        )
        
        # Создание курсов
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание тестового курса',
            owner=self.user_other
        )
    
    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('course-subscribe', kwargs={'course_id': self.course.id})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
    
    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('course-subscribe', kwargs={'course_id': self.course.id})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
