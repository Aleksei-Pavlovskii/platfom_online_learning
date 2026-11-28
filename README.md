# LMS — платформа онлайн-обучения

Django + Django REST Framework проект для онлайн-обучения: курсы, уроки, кастомная модель пользователя, платежи, подписка на обновления курса, оплата через Stripe, права доступа (модераторы / владельцы), фильтрация и сортировка, пагинация, тесты, фоновые задачи (Celery + Redis), рассылка писем подписчикам, периодическая блокировка неактивных пользователей.

## Стек

- Python 3.11+
- Django 5.x
- Django REST Framework 3.15+
- djangorestframework-simplejwt (JWT-авторизация)
- django-filter (фильтрация платежей)
- drf-spectacular (OpenAPI / Swagger / ReDoc)
- stripe (оплата курсов)
- celery + redis (фоновые задачи)
- django-celery-beat (расписание задач)
- PostgreSQL 14+
- psycopg2-binary
- Pillow (для `ImageField`)
- python-dotenv (для переменных окружения)

## Структура проекта

```
platfom_online_learning/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── __init__.py
│   └── wsgi.py / asgi.py
├── lms/
│   ├── migrations/
│   ├── fixtures/
│   ├── management/
│   │   └── commands/
│   │       └── create_moderators_group.py
│   ├── services/
│   │   └── stripe_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_lessons_crud.py
│   │   ├── test_subscriptions.py
│   │   ├── test_stripe.py
│   │   └── test_course_email.py
│   ├── models.py            # Course, Lesson, Subscription
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── paginators.py
│   ├── validators.py
│   ├── tasks.py             # send_course_update_email
│   └── admin.py
├── users/
│   ├── migrations/
│   ├── fixtures/
│   │   └── payments.json
│   ├── management/
│   │   └── commands/
│   │       └── seed_users.py
│   ├── tests/
│   │   └── test_deactivate_inactive_users.py
│   ├── models.py            # User, Payment
│   ├── tasks.py             # deactivate_inactive_users
│   └── admin.py
├── media/                   # загруженные файлы — в .gitignore
├── .env                     # локальные секреты — в .gitignore
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Требования

- **Python** 3.11+
- **PostgreSQL** 14+
- **Redis** (для Celery) — https://redis.io/download
- **Аккаунт Stripe** (для оплаты): https://dashboard.stripe.com/register

Проверка:

```bash
python --version
psql --version
redis-server --version
```

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <url-репозитория>
cd platfom_online_learning
```

### 2. Виртуальное окружение

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> `requirements.txt` должен быть в **UTF-8 без BOM**. Иначе `pip` упадёт с `UnicodeDecodeError`.

### 4. Создать базу данных PostgreSQL

```sql
CREATE DATABASE lms_db;
```

### 5. Настроить `.env`

```powershell
copy .env.example .env        # Windows
cp .env.example .env          # Linux/macOS
```

Заполните `.env`:

```env
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True

DB_NAME=lms_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Stripe (тестовые ключи с https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SUCCESS_URL=http://127.0.0.1:8000/payment/success/?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=http://127.0.0.1:8000/payment/cancel/
STRIPE_CURRENCY=usd

# Email (для разработки — console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@lms.local
```

### 6. Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

> Если используете `django_celery_beat`:
> ```bash
> python manage.py migrate django_celery_beat
> ```

### 7. Суперпользователь

```bash
python manage.py createsuperuser
```

Будут запрошены: `Email`, `First name`, `Last name`, `Password`.

### 8. Тестовые данные (опционально)

```bash
# Группа модераторов
python manage.py create_moderators_group

# Пользователи
python manage.py seed_users

# Платежи (фикстура)
python manage.py loaddata payments
```

**Курс и уроки** (если нет):

```bash
python manage.py shell
```

```python
from lms.models import Course, Lesson
from decimal import Decimal
c = Course.objects.create(title='Алгебра', description='...', price=Decimal('4990.00'))
Lesson.objects.create(course=c, title='Введение', description='...', price=Decimal('490.00'))
Lesson.objects.create(course=c, title='Переменные', description='...', price=Decimal('490.00'))
exit()
```

### 9. Запуск (4 терминала)

#### Терминал 1 — Redis

```bash
redis-server
```

(или Docker: `docker run -p 6379:6379 redis`)

#### Терминал 2 — Celery worker

```bash
celery -A config worker -l info --pool=solo
```

> На Windows — **обязательно** `--pool=solo` (иначе `eventlet`/`gevent` глючат).
> На Linux/macOS — можно без `--pool`.

#### Терминал 3 — Celery beat (планировщик)

```bash
celery -A config beat -l info
```

> `beat` **обязателен** для периодических задач (`CELERY_BEAT_SCHEDULE`). Без него задачи не ставятся.

#### Терминал 4 — Django

```bash
python manage.py runserver
```

- API: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Админка: http://127.0.0.1:8000/admin/

## Переменные окружения

| Переменная | Обязательна | Описание |
|---|---|---|
| `SECRET_KEY` | ✅ | секретный ключ Django |
| `DEBUG` | ⛔ | `True` / `False` |
| `DB_NAME` | ✅ | имя БД PostgreSQL |
| `DB_USER` | ✅ | пользователь БД |
| `DB_PASSWORD` | ✅ | пароль БД |
| `DB_HOST` | ✅ | хост PostgreSQL |
| `DB_PORT` | ✅ | порт PostgreSQL |
| `STRIPE_SECRET_KEY` | ✅ (для оплаты) | `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY` | ✅ (для оплаты) | `pk_test_...` |
| `STRIPE_SUCCESS_URL` | ✅ (для оплаты) | URL после оплаты |
| `STRIPE_CANCEL_URL` | ✅ (для оплаты) | URL после отмены |
| `STRIPE_CURRENCY` | ⛔ | `usd` / `rub` (по умолчанию `usd`) |

`.env` **не коммитится**. В репозитории — только `.env.example`.

## Аутентификация (JWT)

| Метод | URL | Что делает |
|---|---|---|
| POST | `/users/token/` | получить `access` + `refresh` |
| POST | `/users/token/refresh/` | обновить `access` |
| POST | `/users/register/` | регистрация |

Все остальные эндпоинты требуют:

```
Authorization: Bearer <access_token>
```

**Пример логина:**

```http
POST /users/token/
Content-Type: application/json

{"email": "admin@example.com", "password": "testpass123"}
```

→ `200 OK`:

```json
{"access": "eyJ...", "refresh": "eyJ..."}
```

## API — эндпоинты

Базовый URL: `http://127.0.0.1:8000`

### Курсы (ViewSet)

| Метод | URL | Действие |
|---|---|---|
| GET | `/courses/` | список (пагинация, `count_lessons`, `lessons`, `is_subscribed`) |
| POST | `/courses/` | создать |
| GET | `/courses/{id}/` | получить |
| PUT/PATCH | `/courses/{id}/` | обновить (→ рассылка подписчикам) |
| DELETE | `/courses/{id}/` | удалить |

**Права:** модератор — просмотр/редактирование любых, без создания/удаления; владелец — полный доступ к своим.

### Уроки (Generic)

| Метод | URL | Действие |
|---|---|---|
| GET | `/lessons/` | список (пагинация) |
| POST | `/lessons/create/` | создать (только в **свой** курс) |
| GET | `/lessons/{id}/` | получить |
| PUT/PATCH | `/lessons/{id}/update/` | обновить |
| DELETE | `/lessons/{id}/delete/` | удалить |

**Валидация `video_url`:** только `youtube.com` / `youtu.be`.

### Профиль

| Метод | URL | Действие |
|---|---|---|
| GET | `/users/{id}/` | профиль |
| PUT/PATCH | `/users/{id}/` | обновить |
| GET | `/users/{id}/payments/` | профиль + история платежей |

### Платежи

| Метод | URL | Действие |
|---|---|---|
| GET | `/payments/` | список с фильтрацией и сортировкой |

**Параметры:** `?ordering=paid_at` / `-paid_at`, `?course=1`, `?lesson=2`, `?payment_method=cash|transfer|stripe`.

### Подписка

| Метод | URL | Действие |
|---|---|---|
| POST | `/subscriptions/` | toggle: есть — удаляет, нет — создаёт |

**Тело:** `{"course_id": 1}`. Ответ: `{"message": "...", "subscribed": true/false}`.

### Stripe (оплата)

| Метод | URL | Действие |
|---|---|---|
| POST | `/payments/create/` | создать продукт, цену, сессию; сохранить `payment_url` |
| GET | `/payments/{id}/status/` | статус Stripe-сессии + синхронизация `paid_at` |
| GET | `/payment/success/` | callback после оплаты |
| GET | `/payment/cancel/` | callback после отмены |

**Пример:**

```http
POST /payments/create/
Authorization: Bearer <access>
Content-Type: application/json

{"course_id": 1}
```

→ `201 Created`:

```json
{
    "payment_id": 1,
    "amount": "4990.00",
    "payment_url": "https://checkout.stripe.com/c/pay/cs_test_...",
    "session_id": "cs_test_..."
}
```

**Тестовая карта:** `4242 4242 4242 4242`, дата — любая будущая, CVC — любые 3 цифры.

## Права доступа

### Группа `Moderators`

```bash
python manage.py create_moderators_group
```

Права: `view`/`change` для `Course` и `Lesson` (без `add`/`delete`).

Назначение пользователя — **через админку**: `/admin/users/user/` → пользователь → **Groups** → `Moderators`.

### Permission-классы (`lms/permissions.py`)

| Класс | Что делает |
|---|---|
| `IsModerator` | модератор: `GET`/`PUT`/`PATCH` — можно, `POST`/`DELETE` — нельзя |
| `IsOwner` | только владелец объекта |
| `IsModeratorOrOwner` | модератор: просмотр/редактирование; владелец: всё к своим |
| `IsProfileOwnerOrAdmin` | профиль — только владелец или админ |

### Матрица доступа

| Роль | GET | POST | PUT/PATCH | DELETE |
|---|---|---|---|---|
| Аноним | 401 | 401 | 401 | 401 |
| Авторизованный | свои | ✅ (создаёт свои) | свои | свои |
| **Модератор** | все | **403** | все | **403** |
| Админ | все | все | все | все |

## Пагинация

`lms/paginators.py` — `LmsPaginator`:

```python
class LmsPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
```

Параметры: `?page=2`, `?page_size=10`, `?page=999` → 404.

## Валидация ссылок

`lms/validators.py` — `YouTubeUrlValidator`: только `youtube.com` / `youtu.be`. В `LessonSerializer.Meta.validators`.

## Celery — фоновые задачи

### Архитектура

- **Redis** — брокер сообщений и хранилище результатов.
- **Celery worker** — выполняет задачи.
- **Celery beat** — ставит периодические задачи по расписанию.
- **Django** — ставит задачи (`.delay()`) и читает результаты.

### Задача 1 — рассылка подписчикам (`lms/tasks.py`)

```python
@shared_task
def send_course_update_email(course_id):
    """Письмо всем подписчикам курса."""
    from lms.models import Course
    from lms.models import Subscription
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return 0

    emails = list(
        Subscription.objects
        .filter(course=course)
        .values_list('user__email', flat=True)
    )
    if not emails:
        return 0

    send_mail(
        subject=f'Обновление курса: {course.title}',
        message=f'Курс «{course.title}» был обновлён.\n\n{course.description}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
    return len(emails)
```

**Вызов:** в `CourseViewSet.perform_update`:

```python
def perform_update(self, serializer):
    course = serializer.save()
    send_course_update_email.delay(course.id)
```

> Рассылка — **при обновлении** (`PATCH`/`PUT`), не при создании. При создании подписчиков ещё нет.

### Задача 2 — блокировка неактивных (`users/tasks.py`)

```python
@shared_task
def deactivate_inactive_users():
    """Блокирует пользователей, не заходивших > 30 дней."""
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta

    User = get_user_model()
    threshold = timezone.now() - timedelta(days=30)

    updated = User.objects.filter(
        last_login__lt=threshold,
        is_active=True,
    ).update(is_active=False)

    return f'Заблокировано пользователей: {updated}'
```

**Расписание** (`settings.py`):

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'deactivate-inactive-users': {
        'task': 'users.tasks.deactivate_inactive_users',
        'schedule': crontab(hour=3, minute=0),   # каждый день в 03:00
    },
}
```

### Timezone — **критично**

```python
TIME_ZONE = 'UTC'
CELERY_TIMEZONE = TIME_ZONE        # ← должно совпадать!
CELERY_ENABLE_UTC = True
```

Если `TIME_ZONE != CELERY_TIMEZONE` — `crontab(hour=3)` запустится в 03:00 **по `CELERY_TIMEZONE`**, а не по `TIME_ZONE`. Задача будет «не тогда».

### Настройки Celery (`settings.py`)

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
```

### Запуск

```bash
# Терминал 1
redis-server

# Терминал 2
celery -A config worker -l info --pool=solo

# Терминал 3
celery -A config beat -l info

# Терминал 4
python manage.py runserver
```

### Проверка задач

**Рассылка:**

```http
PATCH /courses/1/
Authorization: Bearer <owner>
Content-Type: application/json

{"title": "Алгебра (обновлено)"}
```

В терминале **worker**:

```
Task lms.tasks.send_course_update_email[...] received
[WARNING/ForkPoolWorker-1] Subject: Обновление курса: ...
To: subscriber@example.com
...
Task ... succeeded in 0.05s: 1
```

**Блокировка:**

```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
u = User.objects.create_user(email='old@example.com', password='pass', first_name='Old', last_name='User')
User.objects.filter(pk=u.pk).update(last_login=timezone.now() - timedelta(days=40))
```

Подождите (или временно `crontab(minute='*')`) — в терминале **beat**:

```
Scheduler: Sending due task deactivate-inactive-users
```

В терминале **worker**:

```
Task users.tasks.deactivate_inactive_users[...] received
Task ... succeeded ...: Заблокировано пользователей: 1
```

Проверка:

```python
User.objects.get(email='old@example.com').is_active   # False
```

## Модели

### `User` (`users`)

`AbstractBaseUser` + `PermissionsMixin`. `USERNAME_FIELD = 'email'`. `last_login` — стандартное поле Django, обновляется при логине через `django.contrib.auth.login` / JWT.

### `Course` (`lms`)

`title`, `preview`, `description`, `price`, `owner` (FK).

### `Lesson` (`lms`)

`course` (FK), `title`, `description`, `preview`, `video_url`, `price`, `owner` (FK).

### `Subscription` (`lms`)

`user` (FK), `course` (FK), `created_at`. `UniqueConstraint(user, course)`.

### `Payment` (`users`)

`user` (FK), `paid_at` (nullable), `course` (FK, nullable), `lesson` (FK, nullable), `amount`, `payment_method` (`cash`/`transfer`/`stripe`), `stripe_product_id`, `stripe_price_id`, `stripe_session_id`, `payment_url`.

## Тесты

```bash
python manage.py test lms
python manage.py test users
```

Покрытие:

- **CRUD уроков** — владелец / чужой / модератор / аноним.
- **Подписка** — toggle, 404, 401, `is_subscribed`.
- **Stripe** — моки Stripe, сохранение ID, сумма в центах, ошибка Stripe, синхронизация `paid_at`, чужой платёж.
- **Рассылка** — `mail.outbox`, подписчики, не-подписчики, создание без письма.
- **Блокировка неактивных** — `last_login` > 30 дней → `is_active=False`.

## Запуск с чистого окружения

```bash
python -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1     # Windows
# source .venv-test/bin/activate       # Linux/macOS

pip install -r requirements.txt
copy .env.example .env
# отредактировать .env

python manage.py migrate
python manage.py runserver
```

Если все шаги проходят без ошибок — проект готов к передаче.

## Частые проблемы

### `ModuleNotFoundError: No module named 'django-filter'`

```bash
pip install django-filter
```

В `settings.py` — `'django_filters'` (подчёркивание).

### `AttributeError: 'ellipsis' object has no attribute 'rsplit'`

В `DEFAULT_FILTER_BACKENDS` осталось `...`. Уберите.

### `UnicodeDecodeError` при `pip install -r requirements.txt`

`requirements.txt` в UTF-16. Пересохраните в UTF-8 без BOM.

### `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2` (PostgreSQL)

```bash
pip uninstall psycopg2 psycopg2-binary
pip install "psycopg[binary]"
```

### `Cannot use ImageField because Pillow is not installed`

```bash
pip install Pillow
```

### `models.E015: 'ordering' refers to the nonexistent field`

В `Meta.ordering` — несуществующее поле. Проверьте.

### `loaddata payments`: `ForeignKeyViolation`

Фикстура ссылается на несуществующий `pk`. Проверьте `pk` в БД.

### `loaddata payments`: `Invalid model identifier: lms.payment`

Модель `Payment` в `users` → `"model": "users.payment"`.

### `IntegrityError: значение NULL в столбце "paid_at"`

`paid_at` — `NOT NULL`, а view не передаёт. Сделайте `null=True, blank=True`.

### `404` на `/payment/success/`

Нет маршрута. Добавьте `path('payment/success/', ...)` в `config/urls.py`.

### `NoReverseMatch: 'course-detail' / 'course-subscribe'`

`basename='course'` в роутере (единственное число). Подписка — `subscription-toggle` (если `subscriptions/` с `course_id` в теле).

### `405 Method Not Allowed` на `/courses/{id}/`

`POST` на detail не поддерживается. Для создания — `POST /courses/` (без `{pk}`). Для обновления — `PATCH /courses/{id}/`.

### Stripe API недоступен из РФ

- VPN/прокси на уровне сети.
- `stripe.proxy = 'http://...'` в `stripe_service.py`.
- Деплой на сервер вне РФ.

### Celery: `ConnectionRefusedError` к Redis

Redis не запущен. `redis-server` в отдельном терминале. Проверьте `CELERY_BROKER_URL = 'redis://localhost:6379/0'`.

### Celery: задача `succeeded: 0` (рассылка)

Нет подписчиков у курса. `Subscription.objects.create(user=..., course_id=1)`.

### Celery: `WSAECONNREFUSED` при `send_mail`

SMTP недоступен, а `EMAIL_BACKEND = smtp`. Для проверки — `console.EmailBackend`. **Перезапустите worker** (он читает `settings.py` при старте).

### Celery: `--pool=solo` на Windows

На Windows `eventlet`/`gevent` глючат. Всегда `--pool=solo`.

### Celery beat не ставит задачи

`beat` не запущен. `celery -A config beat -l info` — отдельный терминал. `worker` сам не ставит периодические задачи.

### Задача выполняется «не тогда»

`TIME_ZONE != CELERY_TIMEZONE`. Сделайте одинаковыми: `CELERY_TIMEZONE = TIME_ZONE`.

### `django_celery_beat`: таблиц нет

```bash
python manage.py migrate django_celery_beat
```

## Полезные команды

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Суперпользователь
python manage.py createsuperuser

# Группа модераторов
python manage.py create_moderators_group

# Тестовые пользователи
python manage.py seed_users

# Фикстура платежей
python manage.py loaddata payments

# Тесты
python manage.py test lms
python manage.py test users

# Celery
redis-server
celery -A config worker -l info --pool=solo
celery -A config beat -l info

# Shell
python manage.py shell
```

## Лицензия

Учебный проект. Свободное использование в образовательных целях.