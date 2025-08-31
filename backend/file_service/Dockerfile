# Dockerfile для файлового сервиса
# FastAPI микросервис для управления файлами

FROM python:3.11-slim-bullseye

# Метаданные
LABEL maintainer="Electronic Journal Team"
LABEL description="File service for Electronic Construction Journal"
LABEL version="1.0.0"

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаем пользователя
RUN groupadd -r fastapi && \
    useradd -r -g fastapi fastapi

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    libmagic-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаем директории
RUN mkdir -p /app /app/uploads /app/logs && \
    chown -R fastapi:fastapi /app

WORKDIR /app

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install uvicorn[standard] && \
    pip cache purge

# Копируем код
COPY . .
RUN chown -R fastapi:fastapi /app

# Переключаемся на пользователя
USER fastapi

# Порт
EXPOSE 8001

# Volume для файлов
VOLUME ["/app/uploads", "/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
