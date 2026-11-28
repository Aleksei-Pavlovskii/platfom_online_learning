from decimal import Decimal

from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    preview = models.ImageField(
        upload_to='courses/previews/',
        null=True,
        blank=True,
        verbose_name='Превью'
    )
    description = models.TextField(verbose_name='Описание')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец',
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Цена',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    preview = models.ImageField(
        upload_to='lessons/previews/',
        null=True,
        blank=True,
        verbose_name='Превью',
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Ссылка на видео',
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец',
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Цена',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['title']

    def __str__(self):
        return f'{self.course.title} — {self.title}'



class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_subscription',
            ),
        ]

    def __str__(self):
        return f'{self.user} → {self.course}'
