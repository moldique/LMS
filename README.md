LMS
====

Небольшое учебное API для управления курсами и уроками на Django + DRF.

## Запуск проекта

```bash
# Установка зависимостей
poetry install

# Настройка переменных окружения
# Создайте файл .env в корне проекта и добавьте:
# SECRET_KEY=your-secret-key
# STRIPE_SECRET_KEY=your-stripe-secret-key
# DB_NAME=your-db-name
# DB_USER=your-db-user
# DB_PASSWORD=your-db-password
# DB_HOST=localhost
# DB_PORT=5432

# Применение миграций
poetry run python manage.py migrate

# Загрузка фикстур оплат (опционально)
poetry run python manage.py loaddata user/fixtures/payments.json

# Запуск сервера разработки
poetry run python manage.py runserver
```

Проект доступен по адресу: `http://127.0.0.1:8000/`.

### Настройка Stripe

Для работы с оплатой через Stripe:
1. Зарегистрируйтесь на [Stripe Dashboard](https://dashboard.stripe.com/register)
2. Для тестирования **не подтверждайте аккаунт** — он будет работать в тестовом режиме
3. Получите тестовый Secret Key из панели управления
4. Добавьте его в `.env` файл как `STRIPE_SECRET_KEY`
5. Для тестирования используйте [тестовые карты Stripe](https://stripe.com/docs/terminal/references/testing#standard-test-cards)

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
- Платежи:
  - список/просмотр: `/api/payments/`
  - создание платежа через Stripe: `POST /api/users/payments/create/`
- Пользователи: `/api/users/user/`
- Подписка на курсы: `/api/courses/<course_id>/subscribe/`

## Документация API

Документация API доступна через Swagger и ReDoc:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`
- JSON схема: `http://127.0.0.1:8000/swagger/?format=openapi`

## Дополнительные возможности

### Валидация ссылок

При создании и обновлении уроков проверяется, что поле `video_link` содержит только ссылки на YouTube (youtube.com, www.youtube.com, youtu.be, m.youtube.com). Ссылки на другие ресурсы будут отклонены.

### Подписка на курсы

Пользователи могут подписываться на обновления курсов:
- `POST /api/courses/<course_id>/subscribe/` — подписка/отписка (переключатель).
- При получении данных курса (`GET /api/courses/<id>/`) возвращается поле `is_subscribed`, показывающее статус подписки текущего пользователя.

### Оплата курсов через Stripe

Проект интегрирован с платежной системой Stripe для оплаты курсов:

**Создание платежа:**
```bash
POST /api/users/payments/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "course_id": 1,
  "amount": 100.00
}
```

**Ответ:**
```json
{
  "payment_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "payment_id": 1
}
```

**Как это работает:**
1. Пользователь отправляет запрос с `course_id` и `amount` (сумма в рублях)
2. Система создает продукт в Stripe на основе данных курса
3. Создается цена для продукта
4. Формируется платежная сессия Stripe Checkout
5. Сохраняется запись платежа в базе данных с полями:
   - `stripe_product_id` — ID продукта в Stripe
   - `stripe_price_id` — ID цены в Stripe
   - `stripe_session_id` — ID сессии оплаты
6. Возвращается ссылка на страницу оплаты (`payment_url`)

**Тестирование:**
- Используйте тестовые карты из [документации Stripe](https://stripe.com/docs/terminal/references/testing#standard-test-cards)
- Например: `4242 4242 4242 4242` с любой будущей датой и CVC
- Аккаунт Stripe должен быть в тестовом режиме (не подтвержден)

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
