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
        null=True, blank=True,
        verbose_name='Превью',
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Ссылка на видео',
    )

    def __str__(self):
        return f'{self.course.title} — {self.title}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order','title']
