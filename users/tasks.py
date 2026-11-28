from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    - is_active = False
    - last_login = None (никогда не заходил) — не трогаем (или трогаем, см. ниже)
    """
    threshold = timezone.now() - timedelta(days=30)

    # Только те, кто заходил, но давно
    inactive_users = User.objects.filter(
        last_login__lt=threshold,
        is_active=True,
    )

    count = inactive_users.count()
    updated = inactive_users.update(is_active=False)

    return f'Заблокировано пользователей: {updated} (порог: {threshold.isoformat()})'
