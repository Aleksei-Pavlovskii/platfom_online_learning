from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from lms.models import Subscription


@shared_task
def send_course_update_email(course_id):
    """Celery-задача: письмо подписчикам курса."""
    from lms.models import Course
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return 0

    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    emails = [sub.user.email for sub in subscriptions if sub.user.email]

    if not emails:
        return 0

    send_mail(
        subject=f'Обновление курса: {course.title}',
        message=(
            f'Курс «{course.title}» был обновлён.\n\n'
            f'Описание: {course.description}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
    return len(emails)