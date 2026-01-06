# Используем легковесный образ Python 3.13
FROM python:3.13-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Базовые переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Установить Poetry (глобально)
RUN pip install --no-cache-dir poetry

# Копируем только файлы зависимостей для кеша
COPY pyproject.toml poetry.lock* /app/

# Установить зависимости (без dev-группы)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

# Копируем исходный код приложения в контейнер
COPY . /app

# Создаем директорию для медиафайлов
RUN mkdir -p /app/media

# Пробрасываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]