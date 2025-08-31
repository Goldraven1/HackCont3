# Основной Dockerfile для Django Core Service
# Электронный журнал производства работ - Промышленное решение

# Используем официальный образ Python 3.11 как базовый
FROM python:3.11-slim-bullseye

# Устанавливаем метаданные
LABEL maintainer="Electronic Journal Team"
LABEL description="Core Django service for Electronic Construction Journal"
LABEL version="1.0.0"

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаем пользователя для безопасности
RUN groupadd -r django && \
    useradd -r -g django django

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    # Базовые утилиты
    build-essential \
    curl \
    git \
    # Зависимости для PostgreSQL
    libpq-dev \
    postgresql-client \
    # Зависимости для GIS
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    # Зависимости для обработки изображений
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    # Зависимости для SSL
    libssl-dev \
    libffi-dev \
    # Утилиты для мониторинга
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаем директории приложения
RUN mkdir -p /app /app/logs /app/media /app/static && \
    chown -R django:django /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt requirements-dev.txt ./

# Обновляем pip и устанавливаем Python зависимости
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    # Устанавливаем дополнительные инструменты для продакшена
    pip install gunicorn[gevent] uvicorn[standard] && \
    # Очищаем кеш pip
    pip cache purge

# Копируем код приложения
COPY . .

# Устанавливаем права доступа
RUN chown -R django:django /app && \
    chmod +x /app/docker-entrypoint.sh

# Копируем entrypoint скрипт
COPY docker-entrypoint.sh /app/

# Делаем entrypoint исполняемым
RUN chmod +x /app/docker-entrypoint.sh

# Переключаемся на пользователя django
USER django

# Открываем порт
EXPOSE 8000

# Создаем volume для медиа файлов
VOLUME ["/app/media", "/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Устанавливаем entrypoint и команду по умолчанию
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["prod"]
