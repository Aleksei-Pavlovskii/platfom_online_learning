from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LmsTsetCase(APITestCase):

    def setUp(self):
        self.moderators_group = Group.objects.create(name='Moderators')
        self.owner = User.objects.create_user(
            email='owner@example.com', password='pass12345',
            first_name='Владелец', last_name='Курсов',
        )
        self.other = User.objects.create_user(
            email='other@example.com', password='pass12345',
            first_name='Другой', last_name='Пользователь',
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com', password='pass12345',
            first_name='Мод', last_name='Модератов',
        )
        self.moderator.groups.add(self.moderators_group)

        self.admin = User.objects.create_superuser(
            email='admin@example.com', password='pass12345',
            first_name='Админ', last_name='Админов',
        )
        self.course = Course.objects.create(
            title='Курс владельца', description='...', owner=self.owner,
        )
        self.lesson = Lesson.objects.create(
            course=self.course, title='Урок владельца',
            description='...', owner=self.owner,
        )

    def test_list_lessons_owner_sees_own(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('lms:lessons-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # пагинация: результаты в response.data['results']
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.lesson.pk)

    def test_list_lessons_other_sees_nothing(self):
        self.client.force_authenticate(user=self.other)
        url = reverse('lms:lessons-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 0)

    def test_list_lessons_moderator_sees_all(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lessons-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_list_lessons_anonymous_401(self):
        url = reverse('lms:lessons-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('lms:lesson-retrieve', args=[self.lesson.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lesson.pk)

    def test_retrieve_other_lesson_404(self):
        self.client.force_authenticate(user=self.other)
        url = reverse('lms:lesson-retrieve', args=[self.lesson.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_moderator_sees_any(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lesson-retrieve', args=[self.lesson.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson_owner(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('lms:lesson-create')
        data = {
            'course': self.course.pk,
            'title': 'Новый урок',
            'description': '...',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.owner.pk)
        self.assertTrue(Lesson.objects.filter(title='Новый урок').exists())

    def test_create_lesson_moderator_403(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lesson-create')
        data = {'course': self.course.pk, 'title': 'Новый урок'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_other_can(self):
        self.client.force_authenticate(user=self.other)
        url = reverse('lms:lesson-create')
        data = {'course': self.course.pk, 'title': 'Урок другого'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.other.pk)

    def test_create_lesson_anonymous_401(self):
        url = reverse('lms:lesson-create')
        data = {'course': self.course.pk, 'title': 'Аноним'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('lms:lesson-update', args=[self.lesson.pk])
        response = self.client.patch(url, {'title': 'Обновлён'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновлён')

    def test_update_other_lesson_404(self):
        self.client.force_authenticate(user=self.other)
        url = reverse('lms:lesson-update', args=[self.lesson.pk])
        response = self.client.patch(url, {'title': 'Чужой'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_moderator_any(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lesson-update', args=[self.lesson.pk])
        response = self.client.patch(url, {'title': 'Модератор правил'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_own_lesson(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('lms:lesson-delete', args=[self.lesson.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_delete_other_lesson_404(self):
        self.client.force_authenticate(user=self.other)
        url = reverse('lms:lesson-delete', args=[self.lesson.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_delete_moderator_403(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lesson-delete', args=[self.lesson.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())


class SubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', password='pass12345',
            first_name='Иван', last_name='Иванов',
        )
        self.other = User.objects.create_user(
            email='other@example.com', password='pass12345',
            first_name='Пётр', last_name='Петров',
        )
        self.course = Course.objects.create(
            title='Курс', description='...', owner=self.user,
        )

    def test_subscribe_creates_subscription(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:subscription-toggle')
        response = self.client.post(url, {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['subscribed'])
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_twice_removes_subscription(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:subscription-toggle')

        response = self.client.post(url, {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['subscribed'])

        response = self.client.post(url, {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['subscribed'])
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_without_course_id_400(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:subscription-toggle')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscribe_nonexistent_course_404(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:subscription-toggle')
        response = self.client.post(url, {'course_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_anonymous_401(self):
        url = reverse('lms:subscription-toggle')
        response = self.client.post(url, {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_is_subscribed_true(self):
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse('lms:course-detail', args=[self.course.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_course_is_subscribed_false(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-detail', args=[self.course.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_course_is_subscribed_other_user_false(self):
        Subscription.objects.create(user=self.other, course=self.course)
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-detail', args=[self.course.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

    def test_course_is_subscribed_anonymous_false(self):
        url = reverse('lms:course-detail', args=[self.course.pk])
        response = self.client.get(url)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            return
        self.assertFalse(response.data['is_subscribed'])
