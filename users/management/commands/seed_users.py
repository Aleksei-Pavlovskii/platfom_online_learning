from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей (в группы не добавляет — это в админке)'

    def handle(self, *args, **options):
        users_data = [
            {
                'email': 'moderator@example.com',
                'password': 'moder12345',
                'first_name': 'Мод',
                'last_name': 'Модератов',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'student1@example.com',
                'password': 'student12345',
                'first_name': 'Пётр',
                'last_name': 'Петров',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'student2@example.com',
                'password': 'student12345',
                'first_name': 'Анна',
                'last_name': 'Сидорова',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'admin@example.com',
                'password': 'admin12345',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        created = 0
        for data in users_data:
            email = data.pop('email')
            password = data.pop('password')
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'Уже есть: {email}'))
                continue
            User.objects.create_user(email=email, password=password, **data)
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Создан: {email}'))

        self.stdout.write(self.style.SUCCESS(
            f'Создано: {created} (всего: {User.objects.count()})'
        ))
        self.stdout.write(self.style.NOTICE(
            'Группы назначайте вручную в /admin/ → Users → выбрать пользователя → Groups.'
        ))