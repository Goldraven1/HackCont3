# 3. Структура проекта

## 3.1 Организация файловой системы

```
HackCont3/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
│
├── docs/                           # Документация
│   ├── README.md
│   ├── 01_project_description.md
│   ├── 02_technical_description.md
│   └── ... (остальные файлы документации)
│
├── backend/                        # Backend сервисы
│   ├── core_service/              # Основной Django сервис
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── config/                # Настройки Django
│   │   │   ├── __init__.py
│   │   │   ├── settings/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── development.py
│   │   │   │   ├── production.py
│   │   │   │   └── testing.py
│   │   │   ├── urls.py
│   │   │   ├── wsgi.py
│   │   │   └── asgi.py
│   │   │
│   │   ├── apps/                  # Django приложения
│   │   │   ├── __init__.py
│   │   │   ├── users/            # Управление пользователями
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── views.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── migrations/
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── projects/         # Проекты и объекты
│   │   │   │   ├── models.py
│   │   │   │   ├── views.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── migrations/
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── journal/          # Журнал работ
│   │   │   │   ├── models.py
│   │   │   │   ├── views.py
│   │   │   │   ├── serializers.py
│   │   │   │   ├── urls.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── migrations/
│   │   │   │   └── tests/
│   │   │   │
│   │   │   ├── documents/        # Документооборот
│   │   │   ├── notifications/    # Уведомления
│   │   │   ├── reports/         # Отчеты
│   │   │   └── common/          # Общие компоненты
│   │   │
│   │   ├── static/               # Статические файлы Django
│   │   ├── media/                # Загруженные файлы
│   │   ├── locale/               # Переводы
│   │   └── fixtures/             # Тестовые данные
│   │
│   ├── file_service/             # FastAPI файловый сервис
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── files.py
│   │   │   │   ├── images.py
│   │   │   │   └── documents.py
│   │   │   ├── services/
│   │   │   ├── utils/
│   │   │   └── tests/
│   │   └── storage/              # Локальное хранилище файлов
│   │
│   ├── gis_service/              # FastAPI геолокационный сервис
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── location.py
│   │   │   │   ├── maps.py
│   │   │   │   └── validation.py
│   │   │   ├── services/
│   │   │   ├── utils/
│   │   │   └── tests/
│   │   └── data/                 # Геоданные
│   │
│   └── shared/                   # Общие компоненты backend
│       ├── __init__.py
│       ├── database.py
│       ├── auth.py
│       ├── exceptions.py
│       └── utils.py
│
├── frontend/                     # Frontend приложение
│   ├── index.html
│   ├── css/                      # Стили
│   │   ├── main.css
│   │   ├── components/
│   │   │   ├── header.css
│   │   │   ├── sidebar.css
│   │   │   ├── cards.css
│   │   │   ├── forms.css
│   │   │   ├── tables.css
│   │   │   └── modals.css
│   │   ├── pages/
│   │   │   ├── dashboard.css
│   │   │   ├── journal.css
│   │   │   ├── projects.css
│   │   │   ├── reports.css
│   │   │   └── profile.css
│   │   └── vendor/               # Внешние CSS библиотеки
│   │       ├── bootstrap.min.css
│   │       ├── fontawesome.min.css
│   │       └── leaflet.css
│   │
│   ├── js/                       # JavaScript
│   │   ├── main.js
│   │   ├── config.js
│   │   ├── api/                  # API клиенты
│   │   │   ├── base.js
│   │   │   ├── auth.js
│   │   │   ├── journal.js
│   │   │   ├── files.js
│   │   │   └── gis.js
│   │   ├── components/           # UI компоненты
│   │   │   ├── header.js
│   │   │   ├── sidebar.js
│   │   │   ├── modal.js
│   │   │   ├── datatable.js
│   │   │   ├── map.js
│   │   │   └── file-upload.js
│   │   ├── pages/                # Логика страниц
│   │   │   ├── dashboard.js
│   │   │   ├── journal.js
│   │   │   ├── projects.js
│   │   │   ├── reports.js
│   │   │   └── profile.js
│   │   ├── utils/                # Утилиты
│   │   │   ├── helpers.js
│   │   │   ├── validation.js
│   │   │   ├── formatting.js
│   │   │   └── constants.js
│   │   └── vendor/               # Внешние JS библиотеки
│   │       ├── bootstrap.bundle.min.js
│   │       ├── axios.min.js
│   │       ├── chart.min.js
│   │       ├── leaflet.js
│   │       └── socket.io.min.js
│   │
│   ├── pages/                    # HTML страницы
│   │   ├── dashboard.html
│   │   ├── journal/
│   │   │   ├── index.html
│   │   │   ├── entry.html
│   │   │   └── history.html
│   │   ├── projects/
│   │   │   ├── index.html
│   │   │   ├── detail.html
│   │   │   └── create.html
│   │   ├── documents/
│   │   ├── reports/
│   │   ├── admin/
│   │   └── auth/
│   │       ├── login.html
│   │       ├── register.html
│   │       └── reset-password.html
│   │
│   ├── assets/                   # Медиа ресурсы
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   ├── icons/
│   │   │   └── backgrounds/
│   │   ├── fonts/
│   │   └── documents/
│   │       └── templates/        # Шаблоны документов
│   │
│   └── sw.js                     # Service Worker для PWA
│
├── infrastructure/               # Инфраструктура и деплой
│   ├── docker/
│   │   ├── Dockerfile.django
│   │   ├── Dockerfile.fastapi
│   │   ├── Dockerfile.nginx
│   │   └── docker-compose.prod.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── sites-available/
│   │   └── ssl/
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── ingress/
│   │   └── configmaps/
│   └── scripts/
│       ├── deploy.sh
│       ├── backup.sh
│       └── maintenance.sh
│
├── tests/                        # Тесты
│   ├── backend/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── frontend/
│   │   ├── unit/
│   │   └── e2e/
│   └── performance/
│
├── data/                         # Данные и миграции
│   ├── fixtures/                 # Начальные данные
│   │   ├── users.json
│   │   ├── regions.json
│   │   ├── spgz.json
│   │   └── violations.json
│   ├── migrations/               # Миграции данных
│   ├── samples/                  # Примеры данных
│   │   ├── journals/
│   │   ├── documents/
│   │   └── reports/
│   └── geodata/                  # Геоданные
│       ├── regions.geojson
│       └── objects.geojson
│
└── monitoring/                   # Мониторинг и логи
    ├── prometheus/
    │   └── prometheus.yml
    ├── grafana/
    │   └── dashboards/
    └── logs/
```

## 3.2 Пояснения к структуре

### 3.2.1 Backend организация

**Core Service (Django)**
- Монолитная структура Django с разделением на приложения
- Каждое приложение отвечает за отдельную предметную область
- Конфигурация разделена по окружениям (dev/test/prod)
- Использование Django REST Framework для API

**File Service (FastAPI)**
- Микросервис для работы с файлами
- Асинхронная обработка загрузок
- Интеграция с внешними хранилищами (MinIO/S3)
- Автоматическая оптимизация изображений

**GIS Service (FastAPI)**
- Специализированный сервис для геолокационных данных
- Работа с PostGIS для пространственных запросов
- Валидация координат и проверка присутствия на объекте

### 3.2.2 Frontend организация

**Модульная структура**
- Разделение по компонентам, страницам и утилитам
- Vanilla JavaScript с ES6+ модулями
- CSS организован по компонентам и страницам
- Использование внешних библиотек через CDN или локально

**Progressive Web App (PWA)**
- Service Worker для кэширования и офлайн работы
- Манифест для установки как мобильное приложение
- Поддержка push-уведомлений

### 3.2.3 Infrastructure

**Контейнеризация**
- Отдельные Dockerfile для каждого сервиса
- Docker Compose для локальной разработки
- Kubernetes манифесты для продакшена

**Мониторинг**
- Prometheus для сбора метрик
- Grafana для визуализации
- Centralized logging с ELK stack

### 3.2.4 Данные и тестирование

**Управление данными**
- Fixtures для начальных данных
- Миграции для изменения структуры
- Примеры реальных данных для тестирования

**Тестирование**
- Unit тесты для бизнес-логики
- Integration тесты для API
- E2E тесты для пользовательских сценариев
- Performance тесты для нагрузочного тестирования

## 3.3 Соглашения по именованию

### Backend (Python)
- Модули: `snake_case`
- Классы: `PascalCase`
- Функции/методы: `snake_case`
- Константы: `UPPER_SNAKE_CASE`
- Переменные: `snake_case`

### Frontend (JavaScript)
- Файлы: `kebab-case`
- Функции: `camelCase`
- Классы: `PascalCase`
- Константы: `UPPER_SNAKE_CASE`
- CSS классы: `kebab-case`

### База данных
- Таблицы: `snake_case`
- Поля: `snake_case`
- Индексы: `idx_table_field`
- Foreign keys: `fk_table_field`

## 3.4 Конфигурационные файлы

### Environment файлы
- `.env.development` - Локальная разработка
- `.env.testing` - Тестовое окружение
- `.env.production` - Продакшн окружение

### Docker
- `docker-compose.yml` - Локальная разработка
- `docker-compose.prod.yml` - Продакшн конфигурация

### CI/CD
- `.github/workflows/` - GitHub Actions
- `k8s/` - Kubernetes манифесты

---

*Структура проекта обеспечивает масштабируемость, поддерживаемость и соответствие промышленным стандартам разработки*
