# LMS — платформа онлайн-обучения

Django + Django REST Framework проект для онлайн-обучения: курсы, уроки, кастомная модель пользователя, платежи, подписка на обновления курса, оплата через Stripe, права доступа (модераторы / владельцы), фильтрация и сортировка, пагинация, тесты.

## Стек

- Python 3.11+
- Django 5.x
- Django REST Framework 3.15+
- djangorestframework-simplejwt (JWT-авторизация)
- django-filter (фильтрация платежей)
- stripe (оплата курсов)
- PostgreSQL 14+
- psycopg2-binary
- Pillow (для `ImageField`: preview, avatar)
- python-dotenv (для переменных окружения)

## Структура проекта

```
platfom_online_learning/
├── config/
│   ├── settings.py
│   ├── urls.py
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
│   │   └── test_subscriptions.py
│   ├── models.py            # Course, Lesson, Subscription
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── paginators.py
│   ├── validators.py
│   └── admin.py
├── users/
│   ├── migrations/
│   ├── fixtures/
│   │   └── payments.json
│   ├── management/
│   │   └── commands/
│   │       └── seed_users.py
│   ├── models.py            # User, Payment
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
- **Аккаунт Stripe** (для оплаты): https://dashboard.stripe.com/register

Проверка версий:

```bash
python --version
psql --version
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

Если PowerShell блокирует активацию:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
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

> `requirements.txt` должен быть в кодировке **UTF-8** (без BOM). Иначе `pip` упадёт с `UnicodeDecodeError`.

### 4. Создать базу данных PostgreSQL

```sql
CREATE DATABASE lms_db;
```

Опционально — отдельный пользователь:

```sql
CREATE USER lms_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE lms_db TO lms_user;
```

### 5. Настроить переменные окружения

Скопируйте шаблон:

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
```

> ⚠️ Если в `settings.py` используются имена `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` — переименуйте в `DB_*`. Имена `USER` и `NAME` конфликтуют с переменными окружения ОС.

### 6. Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Суперпользователь

```bash
python manage.py createsuperuser
```

Будут запрошены: `Email`, `First name`, `Last name`, `Password` (модель `User` использует email как логин).

### 8. Тестовые данные (опционально)

**Группа модераторов с правами:**

```bash
python manage.py create_moderators_group
```

**Пользователи:**

```bash
python manage.py seed_users
```

**Курс и уроки** (если нет):

```bash
python manage.py shell
```

```python
from lms.models import Course, Lesson
c = Course.objects.create(title='Алгебра', description='Базовый курс')
Lesson.objects.create(course=c, title='Введение', description='Первый урок')
Lesson.objects.create(course=c, title='Переменные', description='Второй урок')
exit()
```

**Платежи (фикстура):**

```bash
python manage.py loaddata payments
```

> Если `loaddata payments` падает с `ForeignKeyViolation` — проверьте `pk` пользователей/курса/уроков и поправьте `users/fixtures/payments.json`.

### 9. Запуск

```bash
python manage.py runserver
```

- API: http://127.0.0.1:8000/
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
| `STRIPE_SECRET_KEY` | ✅ (для оплаты) | секретный ключ Stripe (`sk_test_...`) |
| `STRIPE_PUBLISHABLE_KEY` | ✅ (для оплаты) | публичный ключ Stripe (`pk_test_...`) |
| `STRIPE_SUCCESS_URL` | ✅ (для оплаты) | URL после успешной оплаты |
| `STRIPE_CANCEL_URL` | ✅ (для оплаты) | URL после отмены оплаты |

`.env` **не коммитится**. В репозитории — только `.env.example`.

## Аутентификация (JWT)

Эндпоинты для получения токенов **открыты** (без авторизации):

| Метод | URL | Что делает |
|---|---|---|
| POST | `/api/token/` | получить `access` + `refresh` по email/паролю |
| POST | `/api/token/refresh/` | обновить `access` по `refresh` |
| POST | `/register/` | регистрация пользователя |

Все остальные эндпоинты требуют заголовок:

```
Authorization: Bearer <access_token>
```

**Пример логина:**

```http
POST /api/token/
Content-Type: application/json

{"email": "admin@example.com", "password": "testpass123"}
```

→ `200 OK`:

```json
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}
```

## API — эндпоинты

Базовый URL: `http://127.0.0.1:8000`

### Курсы (ViewSet — полный CRUD)

| Метод | URL | Действие |
|---|---|---|
| GET | `/courses/` | список курсов (пагинация, `count_lessons`, `lessons`, `is_subscribed`) |
| POST | `/courses/` | создать курс |
| GET | `/courses/{id}/` | получить курс |
| PUT/PATCH | `/courses/{id}/` | обновить курс |
| DELETE | `/courses/{id}/` | удалить курс |

**Права:** модератор — просмотр/редактирование любых, без создания/удаления; владелец — полный доступ к своим; остальные — только свои (через `get_queryset`).

**Пример ответа `GET /courses/`:**

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Алгебра",
            "description": "Базовый курс",
            "preview": null,
            "count_lessons": 2,
            "is_subscribed": true,
            "lessons": [
                {"id": 2, "course": 1, "title": "Введение", "description": "...", "preview": null, "video_url": ""},
                {"id": 3, "course": 1, "title": "Переменные", "description": "...", "preview": null, "video_url": ""}
            ]
        }
    ]
}
```

### Уроки (Generic-классы)

| Метод | URL | Действие |
|---|---|---|
| GET | `/lessons/` | список уроков (пагинация) |
| POST | `/lessons/create/` | создать урок (только в **свой** курс) |
| GET | `/lessons/{id}/` | получить урок |
| PUT/PATCH | `/lessons/{id}/update/` | обновить урок |
| DELETE | `/lessons/{id}/delete/` | удалить урок |

**Права:** как у курсов. При создании `owner` ставится автоматически из `request.user`. Если `course` не принадлежит текущему пользователю → `403`.

**Валидация `video_url`:** разрешены только ссылки на `youtube.com` / `youtu.be` (см. `lms/validators.py`). Ссылки на другие ресурсы → `400`.

**Пример создания урока:**

```http
POST /lessons/create/
Authorization: Bearer <access>
Content-Type: application/json

{
    "course": 1,
    "title": "Введение",
    "description": "Первый урок",
    "video_url": "https://www.youtube.com/watch?v=abc123"
}
```

### Профиль пользователя

| Метод | URL | Действие |
|---|---|---|
| GET | `/users/{id}/` | получить профиль |
| PUT/PATCH | `/users/{id}/` | обновить профиль |
| GET | `/users/{id}/payments/` | профиль + история платежей |

**Пример ответа `GET /users/1/payments/`:**

```json
{
    "id": 1,
    "email": "admin@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "phone": null,
    "city": null,
    "avatar": null,
    "payments": [
        {"id": 3, "paid_at": "2026-11-10T09:15:00+03:00", "course": null, "lesson": 2, "amount": "490.00", "payment_method": "transfer"}
    ]
}
```

### Платежи (список с фильтрацией и сортировкой)

| Метод | URL | Действие |
|---|---|---|
| GET | `/payments/` | список платежей |

**Параметры:**

| Параметр | Пример | Описание |
|---|---|---|
| `ordering` | `?ordering=paid_at` / `?ordering=-paid_at` | сортировка по дате |
| `course` | `?course=1` | фильтр по курсу |
| `lesson` | `?lesson=2` | фильтр по уроку |
| `payment_method` | `?payment_method=cash` / `transfer` / `stripe` | фильтр по способу |

### Подписка на обновления курса

| Метод | URL | Действие |
|---|---|---|
| POST | `/subscriptions/` | toggle: есть подписка — удаляет, нет — создаёт |

**Тело:**

```json
{"course_id": 1}
```

**Ответ:**

```json
{"message": "Подписка добавлена", "subscribed": true}
```

При повторном вызове с тем же `course_id`:

```json
{"message": "Подписка удалена", "subscribed": false}
```

Признак подписки текущего пользователя отдаётся в `CourseSerializer` как поле `is_subscribed`.

### Оплата через Stripe

| Метод | URL | Действие |
|---|---|---|
| POST | `/payments/create/` | создать продукт, цену, сессию в Stripe; сохранить `payment_url` |
| GET | `/payments/{id}/status/` | проверить статус сессии в Stripe |
| GET | `/payment/success/` | редирект после успешной оплаты |
| GET | `/payment/cancel/` | редирект после отмены |

**Пример создания платежа:**

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

Откройте `payment_url` в браузере → страница Stripe → тестовая карта:

| Поле | Значение |
|---|---|
| Номер карты | `4242 4242 4242 4242` |
| Дата | любая будущая (например `12/34`) |
| CVC | любые 3 цифры (например `123`) |

После оплаты — редирект на `STRIPE_SUCCESS_URL`.

**Проверка статуса:**

```http
GET /payments/1/status/
Authorization: Bearer <access>
```

→ `200 OK`:

```json
{
    "payment_id": 1,
    "stripe_status": "complete",
    "stripe_payment_status": "paid",
    "paid_at": "2026-11-26T10:00:00+03:00"
}
```

**Сервисные функции** — в `lms/services/stripe_service.py`:

- `create_stripe_product(name, description)` → dict
- `create_stripe_price(product_id, amount, currency)` → dict (сумма **в центах**)
- `create_stripe_checkout_session(price_id, success_url, cancel_url, metadata)` → dict
- `retrieve_stripe_session(session_id)` → dict

> ⚠️ Сумма передаётся в минимальных единицах: `49.90 usd` → `int(Decimal('49.90') * 100)` = `4990` центов. Валюта — `usd` (бизнес в США).

## Права доступа

### Группа `Moderators`

Создаётся командой:

```bash
python manage.py create_moderators_group
```

Права: `view`/`change` для `Course` и `Lesson` (без `add`/`delete`).

Назначение пользователя в группу — **через админку**: `/admin/users/user/` → пользователь → блок **Groups** → добавить `Moderators` → Save.

### Permission-классы (`lms/permissions.py`)

| Класс | Что делает |
|---|---|
| `IsModerator` | модератор: `GET`/`PUT`/`PATCH` — можно, `POST`/`DELETE` — нельзя |
| `IsOwner` | только владелец объекта |
| `IsModeratorOrOwner` | модератор: просмотр/редактирование; владелец: полный доступ к своим; остальные: 403/404 |
| `IsProfileOwnerOrAdmin` | профиль — только владелец или админ |

### Матрица доступа

| Роль | GET | POST | PUT/PATCH | DELETE |
|---|---|---|---|---|
| Аноним | 401 | 401 | 401 | 401 |
| Авторизованный (не модератор) | свои объекты | ✅ (создаёт свои) | свои объекты | свои объекты |
| **Модератор** | все | **403** | все | **403** |
| Админ (`is_staff`) | все | все | все | все |

## Пагинация

`lms/paginators.py`:

```python
class LmsPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
```

Применяется к `CourseViewSet` и `LessonListAPIView`.

**Параметры:**

- `?page=2` — номер страницы
- `?page_size=10` — размер страницы (макс. 50)
- `?page=999` — `404 Not Found`

## Валидация ссылок

`lms/validators.py` — `YouTubeUrlValidator` разрешает только `youtube.com` / `youtu.be`. Интегрирован в `LessonSerializer.Meta.validators`.

```python
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']
        validators = [YouTubeUrlValidator(field='video_url')]
```

## Модели

### `User` (`users`)

Наследуется от `AbstractBaseUser` + `PermissionsMixin`. `USERNAME_FIELD = 'email'`, `REQUIRED_FIELDS = ['first_name', 'last_name']`. Управляется `UserManager`. Пароль хэшируется через `set_password()`.

### `Course` (`lms`)

`title`, `preview`, `description`, `owner` (FK на `User`, `related_name='courses'`).

### `Lesson` (`lms`)

`course` (FK, `related_name='lessons'`), `title`, `description`, `preview`, `video_url`, `owner` (FK, `related_name='lessons'`).

### `Subscription` (`lms`)

`user` (FK), `course` (FK), `created_at`. `UniqueConstraint(user, course)` — нельзя подписаться дважды.

### `Payment` (`users`)

| Поле | Тип | Примечание |
|---|---|---|
| `user` | FK | `related_name='payments'` |
| `paid_at` | DateTimeField | `null=True, blank=True` — проставляется после оплаты |
| `course` | FK | `null=True, blank=True` |
| `lesson` | FK | `null=True, blank=True` |
| `amount` | DecimalField(10, 2) | `MinValueValidator(0.01)` |
| `payment_method` | CharField | choices: `cash` / `transfer` / `stripe` |
| `stripe_product_id` | CharField | ID продукта в Stripe |
| `stripe_price_id` | CharField | ID цены в Stripe |
| `stripe_session_id` | CharField | ID сессии в Stripe |
| `payment_url` | URLField | ссылка на оплату |

Правило: платёж за **курс** или **урок** (XOR, через `CheckConstraint`).

## Тесты

```bash
python manage.py test lms
```

Покрытие:

- **CRUD уроков** (`test_lessons_crud.py`) — владелец / чужой / модератор / аноним; list / retrieve / create / update / delete.
- **Подписка** (`test_subscriptions.py`) — toggle, 404, 401, `is_subscribed` true/false/чужой.
- Аутентификация — через `self.client.force_authenticate(user=...)`.

Ожидаемо: `Ran 25 tests ... OK`.

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

В `settings.py` — `'django_filters'` (подчёркивание, не дефис).

### `AttributeError: 'ellipsis' object has no attribute 'rsplit'`

В `DEFAULT_FILTER_BACKENDS` осталось `...`. Уберите.

### `UnicodeDecodeError` при `pip install -r requirements.txt`

`requirements.txt` в UTF-16. Пересохраните в UTF-8 без BOM (PyCharm: Convert → UTF-8).

### `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2` (PostgreSQL)

```bash
pip uninstall psycopg2 psycopg2-binary
pip install "psycopg[binary]"
```

### `Cannot use ImageField because Pillow is not installed`

```bash
pip install Pillow
```

### `models.E015: 'ordering' refers to the nonexistent field 'order'`

В `Meta.ordering` указано несуществующее поле. Проверьте имена.

### `loaddata payments`: `ForeignKeyViolation`

Фикстура ссылается на несуществующий `pk`. Проверьте `pk` в БД и поправьте `payments.json`.

### `loaddata payments`: `Invalid model identifier: lms.payment`

Модель `Payment` в `users` → `"model": "users.payment"`.

### `IntegrityError: значение NULL в столбце "paid_at"`

`paid_at` — `NOT NULL`, а view не передаёт дату. Сделайте `paid_at = DateTimeField(null=True, blank=True)` и проставляйте после оплаты.

### `404` на `/payment/success/`

Нет маршрута. Добавьте `path('payment/success/', ...)` в `config/urls.py` (или `lms/urls.py`).

### `NoReverseMatch: 'course-detail' / 'course-subscribe'`

`basename` в роутере — `course` (единственное число). Имя подписки — `subscription-toggle`, если URL `subscriptions/` с `course_id` в теле.

### Stripe API недоступен из РФ

- VPN/прокси на уровне сети.
- `stripe.proxy = 'http://user:pass@proxy-host:port'` в `stripe_service.py`.
- Деплой на сервер вне РФ (Railway, Render, VPS в Европе/США).

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

# Shell
python manage.py shell
```

## Лицензия

Учебный проект. Свободное использование в образовательных целях.