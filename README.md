LMS
====

Небольшое учебное API для управления курсами и уроками на Django + DRF.

## Запуск проекта через Docker Compose

### Требования

- Docker и Docker Compose должны быть установлены
- Файл `.env` должен быть создан на основе `.env.example`

### Быстрый старт

1. **Создайте файл `.env` на основе шаблона:**
   ```bash
   cp .env.example .env
   ```

2. **Заполните переменные окружения в файле `.env`** (особенно `SECRET_KEY`, `DB_PASSWORD`)

3. **Запустите все сервисы:**
   ```bash
   docker-compose up -d
   ```

4. **Примените миграции:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Создайте суперпользователя (опционально):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

Проект будет доступен по адресу: `http://127.0.0.1:8000/`

### Сервисы в Docker Compose

- **web** — Django приложение (порт 8000)
- **db** — PostgreSQL база данных (порт 5432)
- **redis** — Redis для Celery (порт 6379)
- **celery** — Celery worker для выполнения асинхронных задач
- **celery-beat** — Celery beat для выполнения периодических задач

### Проверка работы сервисов

**Проверка Django приложения:**
```bash
# Проверить логи
docker-compose logs web

# Проверить статус
docker-compose ps web

# Открыть в браузере
http://127.0.0.1:8000/swagger/
```

**Проверка базы данных:**
```bash
# Подключиться к PostgreSQL
docker-compose exec db psql -U lms -d lms

# Проверить логи
docker-compose logs db
```

**Проверка Redis:**
```bash
# Подключиться к Redis CLI
docker-compose exec redis redis-cli ping
# Должен вернуть: PONG

# Проверить логи
docker-compose logs redis
```

**Проверка Celery Worker:**
```bash
# Проверить логи
docker-compose logs celery

# Проверить статус
docker-compose ps celery
```

**Проверка Celery Beat:**
```bash
# Проверить логи
docker-compose logs celery-beat

# Проверить статус
docker-compose ps celery-beat
```

### Управление контейнерами

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (очистить данные БД)
docker-compose down -v

# Пересобрать контейнеры после изменений
docker-compose up -d --build

# Просмотр логов всех сервисов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery
```

## Запуск проекта (локально без Docker)

```bash
# Установка зависимостей
poetry install

# Применение миграций
poetry run python manage.py migrate

# Загрузка фикстур оплат (опционально)
poetry run python manage.py loaddata user/fixtures/payments.json

# Запуск сервера разработки
poetry run python manage.py runserver
```

Проект доступен по адресу: `http://127.0.0.1:8000/`.

## Настройка удаленного сервера

Краткий чек-лист для продакшн-сервера:

- Установите: Python, Poetry, PostgreSQL, Redis, Nginx, Git
- Настройте пользователя для деплоя и SSH-ключи
- Откройте порты: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Настройте Gunicorn через `systemd` сервис `lms`
- Настройте Celery worker и Celery Beat через `systemd` сервисы
- Настройте Nginx как reverse proxy и отдачу `/static/` и `/media/`

Пример проверки сервисов:
```bash
sudo systemctl status lms --no-pager
sudo systemctl status lms-celery --no-pager
sudo systemctl status lms-celery-beat --no-pager
sudo systemctl status nginx --no-pager
```

## GitHub Actions: CI/CD

Workflow запускается при `push` в ветку `develop`, прогоняет тесты и выполняет деплой.

### Secrets для GitHub Actions

Добавьте Secrets в репозиторий:

- `SSH_HOST` — IP или домен сервера
- `SSH_USER` — пользователь на сервере (например, `lmsuser`)
- `SSH_KEY` — приватный SSH-ключ
- `SSH_PORT` — порт SSH (обычно `22`)

### Как работает деплой

1. Делаете `git push` в ветку `develop`.
2. Запускается workflow: установка зависимостей и тесты.
3. После успешных тестов выполняется SSH-деплой на сервер:
   - `git pull origin develop`
   - `poetry install`
   - `migrate`, `collectstatic`
   - перезапуск `systemd` сервисов и `nginx`

Проверка статуса на сервере:
```bash
sudo systemctl status lms --no-pager
```

## Настройка Celery и Redis (локальный запуск)

Проект использует Celery для асинхронных задач и периодических заданий.

### Требования

- Redis должен быть установлен и запущен
- Для Windows рекомендуется использовать пул `eventlet`

### Переменные окружения

Создайте файл `.env` в корне проекта и добавьте:

```env
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
DEFAULT_FROM_EMAIL=noreply@lms.com
```

### Запуск Celery Worker

В отдельном терминале:

```bash
# Для Windows (с eventlet)
poetry run celery -A config worker --pool=eventlet -l info

# Для Linux/Mac
poetry run celery -A config worker -l info
```

### Запуск Celery Beat (для периодических задач)

В отдельном терминале:

```bash
poetry run celery -A config beat -l info
```

**Важно:** На Windows используйте `127.0.0.1` вместо `localhost` для подключения к Redis.

## Аутентификация и пользователи

- Авторизация по JWT.
- Получение токена:
  - `POST /api/token/` — передать `email` и `password`.
  - `POST /api/token/refresh/` — обновление access-токена.
- Регистрация:
  - `POST /api/users/register/`.

По умолчанию все API защищены `IsAuthenticated`, кроме регистрации и получения токена.

## Роли и права доступа

- Группа **moderators**:
  - может просматривать и редактировать любые курсы и уроки;
  - не может создавать и удалять курсы и уроки.
- Обычный пользователь:
  - видит только свои курсы и уроки;
  - может создавать, редактировать и удалять только свои объекты.

## Основные эндпоинты

- Курсы: `/api/courses/`
- Уроки:
  - список/создание: `/api/lessons/`
  - детали/редактирование/удаление: `/api/lessons/<id>/`
- Платежи: `/api/payments/`
- Пользователи: `/api/users/user/`
- Подписка на курсы: `/api/courses/<course_id>/subscribe/`

## Дополнительные возможности

### Валидация ссылок

При создании и обновлении уроков проверяется, что поле `video_link` содержит только ссылки на YouTube (youtube.com, www.youtube.com, youtu.be, m.youtube.com). Ссылки на другие ресурсы будут отклонены.

### Подписка на курсы

Пользователи могут подписываться на обновления курсов:
- `POST /api/courses/<course_id>/subscribe/` — подписка/отписка (переключатель).
- При получении данных курса (`GET /api/courses/<id>/`) возвращается поле `is_subscribed`, показывающее статус подписки текущего пользователя.

### Асинхронная email рассылка

При обновлении курса все подписчики автоматически получают email-уведомление:
- Email отправляется асинхронно через Celery
- При обновлении урока уведомление отправляется только если курс не обновлялся более 4 часов
- Для разработки email выводится в консоль (настройка `EMAIL_BACKEND` в `settings.py`)

### Пагинация

Списки курсов и уроков поддерживают пагинацию:
- По умолчанию: 10 элементов на странице.
- Параметры запроса:
  - `?page=1` — номер страницы.
  - `?page_size=20` — количество элементов на странице (максимум 50).

### Тестирование

Для запуска тестов:
```bash
poetry run python manage.py test lms.tests
```

Для проверки покрытия тестами:
```bash
poetry run coverage run --source='lms' manage.py test lms.tests
poetry run coverage report
poetry run coverage html -d coverage_report
```

Текущее покрытие кода тестами: **90%**.

## Периодические задачи

Проект использует celery-beat для выполнения периодических задач:

- **Блокировка неактивных пользователей**: выполняется каждый день в 00:00 UTC
  - Блокирует пользователей (`is_active=False`), которые не входили в систему более 30 дней
  - Задача: `user.tasks.block_inactive_users`

## Технические детали

### Celery

- Используется пул `eventlet` для Windows
- Автоматическое обнаружение задач из `lms/tasks.py` и `user/tasks.py`
- Настройки Redis вынесены в переменные окружения

### Email

- По умолчанию используется консольный бэкенд для разработки
- Для продакшена настройте SMTP в `settings.py` и переменных окружения
