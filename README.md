# LMS — платформа онлайн-обучения

Django + Django REST Framework проект для онлайн-обучения: курсы, уроки, кастомная модель пользователя и платежи. Реализован CRUD для курсов (ViewSet), уроков (Generic-классы), профиля пользователя (RetrieveUpdateAPIView), список платежей с фильтрацией и сортировкой, а также история платежей в профиле пользователя.

## Стек

- Python 3.11+
- Django 5.x
- Django REST Framework 3.15+
- django-filter (фильтрация платежей)
- PostgreSQL 14+
- psycopg2-binary
- Pillow (для `ImageField`: preview, avatar)
- python-dotenv (для переменных окружения)

## Структура проекта

```
platfom_online_learning/
├── config/                 # настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── lms/                    # приложение LMS: курсы и уроки
│   ├── migrations/
│   ├── fixtures/
│   ├── models.py           # Course, Lesson
│   ├── serializers.py      # CourseSerializer, LessonSerializer, PaymentSerializer, UserSerializer, UserPaymentSerializer
│   ├── views.py            # CourseViewSet, Lesson*APIView, PaymentListAPIView, User*APIView
│   ├── urls.py             # маршруты приложения
│   └── admin.py
├── users/                  # приложение пользователей и платежей
│   ├── migrations/
│   ├── fixtures/
│   │   └── payments.json   # фикстура платежей
│   ├── models.py           # User, Payment
│   └── admin.py
├── media/                  # загруженные файлы (preview, avatar) — в .gitignore
├── .env                    # локальные секреты — в .gitignore
├── .env.example            # шаблон переменных окружения
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Требования

- **Python** 3.11 или выше
- **PostgreSQL** 14 или выше (запущенный сервер)
- **pip** и **venv** (идут с Python)

Проверка версий:

```bash
python --version
psql --version
```

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone <https://github.com/Aleksei-Pavlovskii/platfom_online_learning.git>
cd platfom_online_learning
```

### 2. Создать и активировать виртуальное окружение

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если PowerShell блокирует активацию:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Windows (cmd):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
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

> `requirements.txt` должен быть в кодировке **UTF-8** (без BOM). Если pip ругается на `UnicodeDecodeError` — пересохраните файл в UTF-8.

### 4. Создать базу данных PostgreSQL

Подключитесь к серверу PostgreSQL (`psql -U postgres`) и выполните:

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

**Windows:**

```powershell
copy .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Откройте `.env` и заполните значения:

```env
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True

NAME=lms_db
USER=postgres
PASSWORD=your_password
HOST=127.0.0.1
PORT=5432
```

> ⚠️ Если в `settings.py` используются имена `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` — переименуйте их в `DB_*`. Имена `USER` и `NAME` конфликтуют со стандартными переменными окружения ОС и могут привести к неожиданному подключению.

### 6. Применить миграции

```bash
python manage.py migrate
```

### 7. Создать суперпользователя

```bash
python manage.py createsuperuser
```

Будут запрошены: `Email`, `First name`, `Last name`, `Password` (модель `User` использует email как логин).

### 8. Загрузить тестовые данные (опционально)

Фикстура платежей требует существующих пользователей, курса и уроков. Создайте их:

**Пользователи (3 шт.):**

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(email='admin@example.com', password='testpass123', first_name='Иван', last_name='Иванов', is_staff=True, is_superuser=True)
User.objects.create_user(email='student1@example.com', password='testpass123', first_name='Пётр', last_name='Петров')
User.objects.create_user(email='student2@example.com', password='testpass123', first_name='Анна', last_name='Сидорова')
exit()
```

**Курс и уроки:**

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

**Платежи:**

```bash
python manage.py loaddata payments
```

Ожидаемый вывод:

```
Installed 4 object(s) from 1 fixture(s)
```

> Если `loaddata payments` падает с `ForeignKeyViolation` — проверьте, что `pk` пользователей/курса/уроков в фикстуре совпадают с реальными `pk` в БД:
> ```python
> from django.contrib.auth import get_user_model
> from lms.models import Course, Lesson
> print(list(get_user_model().objects.values_list('pk', 'email')))
> print(list(Course.objects.values_list('pk', 'title')))
> print(list(Lesson.objects.values_list('pk', 'title')))
> ```
> Поправьте `user`/`course`/`lesson` в `users/fixtures/payments.json` под реальные `pk`.

### 9. Запустить сервер разработки

```bash
python manage.py runserver
```

Проект доступен по адресу: <http://127.0.0.1:8000/>

Админка: <http://127.0.0.1:8000/admin/>

## Переменные окружения

Все переменные читаются из `.env` в корне проекта (через `python-dotenv`).

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `SECRET_KEY` | ✅ | секретный ключ Django | `django-insecure-...` |
| `DEBUG` | ⛔ | режим отладки | `True` / `False` |
| `DB_NAME` | ✅ | имя базы данных PostgreSQL | `lms_db` |
| `DB_USER` | ✅ | пользователь БД | `postgres` |
| `DB_PASSWORD` | ✅ | пароль пользователя БД | `your_password` |
| `DB_HOST` | ✅ | хост PostgreSQL | `127.0.0.1` |
| `DB_PORT` | ✅ | порт PostgreSQL | `5432` |

Файл `.env` **не коммитится** в репозиторий (см. `.gitignore`). В репозитории хранится только `.env.example` с плейсхолдерами.

## API — эндпоинты

Базовый URL: `http://127.0.0.1:8000`

### Курсы (ViewSet — полный CRUD)

| Метод | URL | Действие |
|---|---|---|
| GET | `/courses/` | список курсов (с `count_lessons` и `lessons`) |
| POST | `/courses/` | создать курс |
| GET | `/courses/{id}/` | получить курс |
| PUT | `/courses/{id}/` | обновить курс |
| PATCH | `/courses/{id}/` | частично обновить курс |
| DELETE | `/courses/{id}/` | удалить курс |

**Пример создания курса:**

```http
POST /courses/
Content-Type: application/json

{
    "title": "Python для начинающих",
    "description": "Базовый курс по Python"
}
```

**Пример ответа `GET /courses/`:**

```json
[
    {
        "id": 1,
        "title": "Алгебра",
        "preview": null,
        "description": "Базовый курс",
        "count_lessons": 2,
        "lessons": [
            {"id": 2, "course": 1, "title": "Введение", "description": "Первый урок", "preview": null, "video_url": ""},
            {"id": 3, "course": 1, "title": "Переменные", "description": "Второй урок", "preview": null, "video_url": ""}
        ]
    }
]
```

### Уроки (Generic-классы)

| Метод | URL | Действие |
|---|---|---|
| GET | `/lessons/` | список уроков |
| POST | `/lessons/create/` | создать урок |
| GET | `/lessons/{id}/` | получить урок |
| PUT | `/lessons/{id}/update/` | обновить урок |
| DELETE | `/lessons/{id}/delete/` | удалить урок |

**Пример создания урока:**

```http
POST /lessons/create/
Content-Type: application/json

{
    "course": 1,
    "title": "Введение",
    "description": "Первый урок",
    "video_url": "https://example.com/video"
}
```

### Профиль пользователя

| Метод | URL | Действие |
|---|---|---|
| GET | `/users/{id}/` | получить профиль |
| PUT | `/users/{id}/` | полностью обновить профиль |
| PATCH | `/users/{id}/` | частично обновить профиль |

**Пример частичного обновления:**

```http
PATCH /users/1/
Content-Type: application/json

{
    "first_name": "Иван",
    "city": "Москва"
}
```

> Поле `password` через API профиля не редактируется. Для смены пароля предусмотрен отдельный эндпоинт (в текущей версии не реализован).

### История платежей в профиле

| Метод | URL                     | Действие |
|---|-------------------------|---|
| GET | `/users/{pk}/payments/` | профиль + история платежей |

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
        {
            "id": 3,
            "user": 1,
            "paid_at": "2026-11-10T09:15:00+03:00",
            "course": null,
            "lesson": 2,
            "amount": "490.00",
            "payment_method": "transfer"
        },
        {
            "id": 1,
            "user": 1,
            "paid_at": "2026-11-01T10:00:00+03:00",
            "course": 1,
            "lesson": null,
            "amount": "4990.00",
            "payment_method": "transfer"
        }
    ]
}
```

> Если у вас старый маршрут `user/{id}/` — он тоже работает, но рекомендуется `users/{id}/payments/`.

### Платежи (список с фильтрацией и сортировкой)

| Метод | URL | Действие |
|---|---|---|
| GET | `/payments/` | список платежей (с фильтрацией и сортировкой) |

**Параметры запроса:**

| Параметр | Пример | Описание |
|---|---|---|
| `ordering` | `?ordering=paid_at` или `?ordering=-paid_at` | сортировка по дате оплаты |
| `course` | `?course=1` | фильтр по курсу |
| `lesson` | `?lesson=2` | фильтр по уроку |
| `payment_method` | `?payment_method=cash` / `transfer` | фильтр по способу оплаты |

**Примеры:**

```
GET /payments/
GET /payments/?ordering=-paid_at
GET /payments/?course=1
GET /payments/?lesson=2
GET /payments/?payment_method=cash
GET /payments/?payment_method=transfer&ordering=paid_at
```

**Пример ответа:**

```json
[
    {
        "id": 4,
        "user": 3,
        "paid_at": "2026-11-12T18:45:00+03:00",
        "course": null,
        "lesson": 3,
        "amount": "490.00",
        "payment_method": "cash"
    },
    {
        "id": 2,
        "user": 2,
        "paid_at": "2026-11-05T14:30:00+03:00",
        "course": 1,
        "lesson": null,
        "amount": "4990.00",
        "payment_method": "cash"
    }
]
```

## Модели

### `User` (кастомная, приложение `users`)

Наследуется от `AbstractBaseUser` + `PermissionsMixin`.

| Поле | Тип | Примечание |
|---|---|---|
| `email` | `EmailField` | `unique=True`, `USERNAME_FIELD` |
| `first_name` | `CharField(20)` | `REQUIRED_FIELDS` |
| `last_name` | `CharField(30)` | `REQUIRED_FIELDS` |
| `phone` | `CharField(20)` | необязательное |
| `city` | `CharField(30)` | необязательное |
| `avatar` | `ImageField` | необязательное |
| `is_active` | `BooleanField` | по умолчанию `True` |
| `is_staff` | `BooleanField` | по умолчанию `False` |

Управляется через `UserManager` (`create_user`, `create_superuser`). Пароль хэшируется через `set_password()`.

### `Course` (приложение `lms`)

| Поле | Тип |
|---|---|
| `title` | `CharField(100)` |
| `preview` | `ImageField` (необязательное) |
| `description` | `TextField` |

Сортировка: по `title`.

### `Lesson` (приложение `lms`)

| Поле | Тип | Примечание |
|---|---|---|
| `course` | `ForeignKey(Course)` | `on_delete=CASCADE`, `related_name='lessons'` |
| `title` | `CharField(200)` | |
| `description` | `TextField` | необязательное |
| `preview` | `ImageField` | необязательное |
| `video_url` | `URLField(500)` | необязательное |

### `Payment` (приложение `users`)

| Поле | Тип | Примечание |
|---|---|---|
| `user` | `ForeignKey(AUTH_USER_MODEL)` | `on_delete=CASCADE`, `related_name='payments'` |
| `paid_at` | `DateTimeField` | дата и время оплаты |
| `course` | `ForeignKey(Course)` | `null=True, blank=True`, `related_name='payments'` |
| `lesson` | `ForeignKey(Lesson)` | `null=True, blank=True`, `related_name='payments'` |
| `amount` | `DecimalField(10, 2)` | `MinValueValidator(0.01)` |
| `payment_method` | `CharField(20)` | choices: `cash` / `transfer` |

Правило: платёж относится **либо** к курсу, **либо** к уроку (XOR). Может быть ограничено `CheckConstraint` на уровне БД.

Сортировка: `-paid_at` (свежие сверху).

## Проверка работоспособности

### Через браузер

- <http://127.0.0.1:8000/admin/> — админка (после `createsuperuser`)
- <http://127.0.0.1:8000/courses/> — список курсов (JSON)
- <http://127.0.0.1:8000/lessons/> — список уроков (JSON)
- <http://127.0.0.1:8000/payments/> — список платежей (JSON)
- <http://127.0.0.1:8000/users/1/payments/> — профиль с платежами

### Через curl

```bash
# Список курсов
curl http://127.0.0.1:8000/courses/

# Создать курс
curl -X POST http://127.0.0.1:8000/courses/ \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Python\", \"description\": \"Базовый курс\"}"

# Создать урок
curl -X POST http://127.0.0.1:8000/lessons/create/ \
  -H "Content-Type: application/json" \
  -d "{\"course\": 1, \"title\": \"Введение\"}"

# Список платежей с фильтрацией
curl "http://127.0.0.1:8000/payments/?payment_method=cash&ordering=-paid_at"
```

### Через Postman

1. Создайте коллекцию `LMS`.
2. Добавьте запросы из таблиц выше.
3. Для POST/PUT/PATCH — `Body → raw → JSON`.

## Запуск с чистого окружения (проверка)

Чтобы убедиться, что проект поднимается «с нуля»:

```bash
# 1. Новый venv
python -m venv .venv-test
.\.venv-test\Scripts\Activate.ps1     # Windows
# source .venv-test/bin/activate       # Linux/macOS

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка .env
copy .env.example .env
# отредактировать .env

# 4. Миграции и запуск
python manage.py migrate
python manage.py runserver
```

Если все шаги проходят без ошибок — проект готов к передаче.

## Частые проблемы

### `ModuleNotFoundError: No module named 'django-filter'`

Пакет не установлен или неверно указан в `INSTALLED_APPS`.

```bash
pip install django-filter
```

В `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_filters',   # ← подчёркивание, не дефис
]
```

И в `REST_FRAMEWORK` **не должно быть** `...` (Ellipsis):

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
}
```

### `AttributeError: 'ellipsis' object has no attribute 'rsplit'`

В `DEFAULT_FILTER_BACKENDS` осталось многоточие `...`. Уберите его — это не «пропуск», а объект `Ellipsis`, который DRF пытается импортировать как backend.

### `UnicodeDecodeError` при `pip install -r requirements.txt`

`requirements.txt` сохранён в UTF-16 (типично для PowerShell). Пересохраните файл в **UTF-8 без BOM**:

- **PyCharm:** внизу справа кликните на кодировку → *Convert → UTF-8*.
- **PowerShell:** `[System.IO.File]::WriteAllLines("$PWD\requirements.txt", (Get-Content .\requirements.txt -Encoding Unicode), [System.Text.UTF8Encoding]::new($false))`

### `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2` при подключении к PostgreSQL

Проблема кодировки клиента. Попробуйте:

```bash
pip uninstall psycopg2 psycopg2-binary
pip install "psycopg[binary]"
```

Или добавьте в `settings.py`:

```python
DATABASES['default']['OPTIONS'] = {'options': '-c client_encoding=utf8'}
```

### `Cannot use ImageField because Pillow is not installed`

```bash
pip install Pillow
```

### `django.db.utils.OperationalError: could not connect to server`

- Проверьте, что PostgreSQL запущен.
- Проверьте `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` в `.env`.
- Убедитесь, что БД `lms_db` создана (`CREATE DATABASE lms_db;`).

### `InconsistentMigrationHistory` после смены `AUTH_USER_MODEL`

Если БД создавалась со стандартной `auth.User`, а потом вы подключили кастомную — пересоздайте БД:

```bash
# удалить db.sqlite3 (если SQLite) или DROP DATABASE lms_db; CREATE DATABASE lms_db;
python manage.py makemigrations
python manage.py migrate
```

### `models.E015: 'ordering' refers to the nonexistent field 'order'`

В `Meta.ordering` указано поле, которого нет в модели. Проверьте, что все имена в `ordering` реально существуют (например, `paid_at`, а не `payment_at`).

### `loaddata payments`: `ForeignKeyViolation: Ключ (lesson_id)=(1) отсутствует в таблице`

Фикстура ссылается на несуществующий `pk`. Проверьте реальные `pk` пользователей, курсов и уроков и поправьте `users/fixtures/payments.json`:

```python
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson
print(list(get_user_model().objects.values_list('pk', 'email')))
print(list(Course.objects.values_list('pk', 'title')))
print(list(Lesson.objects.values_list('pk', 'title')))
```

### `loaddata payments`: `Invalid model identifier: lms.payment`

Модель `Payment` находится в приложении `users`. В фикстуре должно быть:

```json
"model": "users.payment"
```

### `RuntimeWarning: DateTimeField Payment.paid_at received a naive datetime`

В фикстуре `paid_at` указан без времени/зоны (`"2026-11-01"`), а поле — `DateTimeField` при `USE_TZ=True`. Используйте ISO с часовым поясом:

```json
"paid_at": "2026-11-01T10:00:00+03:00"
```

Или смените тип поля на `DateField`, если достаточно только даты.

## Полезные команды

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Откатить последнюю миграцию приложения
python manage.py migrate lms zero

# Создать суперпользователя
python manage.py createsuperuser

# Загрузить фикстуру
python manage.py loaddata payments

# Открыть Django shell
python manage.py shell

# Собрать статику (для production)
python manage.py collectstatic
```

## Лицензия

Учебный проект. Свободное использование в образовательных целях.