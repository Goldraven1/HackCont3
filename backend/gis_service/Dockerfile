# Dockerfile для GIS сервиса
# FastAPI микросервис для геопространственных данных

FROM python:3.11-slim-bullseye

# Метаданные
LABEL maintainer="Electronic Journal Team"
LABEL description="GIS service for Electronic Construction Journal"
LABEL version="1.0.0"

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаем пользователя
RUN groupadd -r gis && \
    useradd -r -g gis gis

# Устанавливаем системные зависимости для GIS
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    proj-bin \
    proj-data \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаем директории
RUN mkdir -p /app /app/logs && \
    chown -R gis:gis /app

WORKDIR /app

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install uvicorn[standard] && \
    pip cache purge

# Копируем код
COPY . .
RUN chown -R gis:gis /app

# Переключаемся на пользователя
USER gis

# Порт
EXPOSE 8002

# Volume для логов
VOLUME ["/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
