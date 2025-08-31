#!/bin/bash
set -e

# Функция для логирования
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Ожидание готовности базы данных
wait_for_db() {
    log "Waiting for PostgreSQL to be ready..."
    while ! pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do
        log "PostgreSQL is not ready. Waiting..."
        sleep 2
    done
    log "PostgreSQL is ready!"
}

# Ожидание готовности Redis
wait_for_redis() {
    log "Waiting for Redis to be ready..."
    while ! timeout 1 bash -c "echo > /dev/tcp/${REDIS_HOST:-redis}/${REDIS_PORT:-6379}"; do
        log "Redis is not ready. Waiting..."
        sleep 2
    done
    log "Redis is ready!"
}

# Инициализация базы данных
init_db() {
    log "Running database migrations..."
    python manage.py migrate --noinput
    
    log "Creating superuser if not exists..."
    python manage.py shell << 'PYTHON'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@electronic-journal.local',
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123!')
    )
    print("Superuser created")
else:
    print("Superuser already exists")
PYTHON

    log "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    log "Loading initial data..."
    python manage.py loaddata initial_data.json || true
}

# Функция для запуска сервера разработки
run_dev() {
    log "Starting Django development server..."
    python manage.py runserver 0.0.0.0:8000
}

# Функция для запуска продакшн сервера
run_prod() {
    log "Starting Django production server with Gunicorn..."
    exec gunicorn core_service.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --worker-class gevent \
        --worker-connections ${GUNICORN_WORKER_CONNECTIONS:-1000} \
        --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
        --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-100} \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level ${LOG_LEVEL:-info} \
        --capture-output \
        --enable-stdio-inheritance
}

# Функция для запуска Celery worker
run_celery_worker() {
    log "Starting Celery worker..."
    exec celery -A core_service worker \
        --loglevel=${CELERY_LOG_LEVEL:-info} \
        --concurrency=${CELERY_WORKERS:-4} \
        --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD:-1000} \
        --prefetch-multiplier=${CELERY_PREFETCH_MULTIPLIER:-1}
}

# Функция для запуска Celery beat
run_celery_beat() {
    log "Starting Celery beat scheduler..."
    exec celery -A core_service beat \
        --loglevel=${CELERY_LOG_LEVEL:-info} \
        --schedule=/app/celerybeat-schedule \
        --pidfile=/app/celerybeat.pid
}

# Функция для запуска Celery flower
run_celery_flower() {
    log "Starting Celery Flower monitoring..."
    exec celery -A core_service flower \
        --port=5555 \
        --broker=${CELERY_BROKER_URL:-redis://redis:6379/0}
}

# Основная логика
case "$1" in
    "dev")
        wait_for_db
        wait_for_redis
        init_db
        run_dev
        ;;
    "prod")
        wait_for_db
        wait_for_redis
        init_db
        run_prod
        ;;
    "celery-worker")
        wait_for_db
        wait_for_redis
        run_celery_worker
        ;;
    "celery-beat")
        wait_for_db
        wait_for_redis
        run_celery_beat
        ;;
    "celery-flower")
        wait_for_redis
        run_celery_flower
        ;;
    "migrate")
        wait_for_db
        python manage.py migrate
        ;;
    "collectstatic")
        python manage.py collectstatic --noinput --clear
        ;;
    "shell")
        wait_for_db
        python manage.py shell
        ;;
    "test")
        wait_for_db
        python manage.py test
        ;;
    *)
        log "Starting with custom command: $@"
        exec "$@"
        ;;
esac
