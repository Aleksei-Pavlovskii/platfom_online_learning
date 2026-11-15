# LMS — платформа онлайн-обучения

Django + Django REST Framework проект для онлайн-обучения: курсы, уроки и кастомная модель пользователя. Реализован CRUD для курсов (ViewSet), уроков (Generic-классы) и профиля пользователя (RetrieveUpdateAPIView).

## Стек

- Python 3.11+
- Django 5.x
- Django REST Framework 3.15+
- PostgreSQL 14+
- psycopg2-binary
- Pillow (для `ImageField`)
- python-dotenv (для переменных окружения)

## Структура проекта

```
platfom_online_learning/
├── config/                 # настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── lms/                    # приложение LMS
│   ├── migrations/
│   ├── models.py           # Course, Lesson, User
│   ├── serializers.py      # CourseSerializer, LessonSerializer, UserSerializer
│   ├── views.py            # CourseViewSet, Lesson*APIView, UserRetrieveUpdateAPIView
│   ├── urls.py             # маршруты приложения
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
git clone <url-репозитория>
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
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_DEBUG=True

DB_NAME=lms_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 6. Применить миграции

```bash
python manage.py migrate
```

### 7. Создать суперпользователя

```bash
python manage.py createsuperuser
```

Будут запрошены: `Email`, `First name`, `Last name`, `Password` (модель `User` использует email как логин).

### 8. Запустить сервер разработки

```bash
python manage.py runserver
```

Проект доступен по адресу: <http://127.0.0.1:8000/>

Админка: <http://127.0.0.1:8000/admin/>

## Переменные окружения

Все переменные читаются из `.env` в корне проекта (через `python-dotenv`).

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | ✅ | секретный ключ Django | `django-insecure-...` |
| `DJANGO_DEBUG` | ⛔ | режим отладки | `True` / `False` |
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
| GET | `/courses/` | список курсов |
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

### Профиль пользователя (RetrieveUpdateAPIView)

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

## Модели

### `User` (кастомная)

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

### `Course`

| Поле | Тип |
|---|---|
| `title` | `CharField(100)` |
| `preview` | `ImageField` (необязательное) |
| `description` | `TextField` |

Сортировка: по `title`.

### `Lesson`

| Поле | Тип | Примечание |
|---|---|---|
| `course` | `ForeignKey(Course)` | `on_delete=CASCADE`, `related_name='lessons'` |
| `title` | `CharField(200)` | |
| `description` | `TextField` | необязательное |
| `preview` | `ImageField` | необязательное |
| `video_url` | `URLField(500)` | необязательное |
| `order` | `PositiveIntegerField` | порядок в курсе |

Сортировка: по `order`, затем `title`.

## Проверка работоспособности

### Через браузер

- <http://127.0.0.1:8000/admin/> — админка (после `createsuperuser`)
- <http://127.0.0.1:8000/courses/> — список курсов (JSON)
- <http://127.0.0.1:8000/lessons/> — список уроков (JSON)

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

В `Meta.ordering` указано поле, которого нет в модели. Добавьте поле `order` в `Lesson` или уберите его из `ordering`.

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

# Открыть Django shell
python manage.py shell

# Собрать статику (для production)
python manage.py collectstatic

# Список URL
python manage.py show_urls  # требует django-extensions
```

## Лицензия

Учебный проект. Свободное использование в образовательных целях.