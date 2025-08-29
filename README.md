# Электронный журнал производства работ на объектах благоустройства

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-blue.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)

## Обзор проекта

Промышленное решение для автоматизации ведения исполнительной документации на объектах благоустройства. Система объединяет работу различных контролирующих органов в едином интерфейсе с обязательной геолокационной привязкой.

### Ключевые особенности

- 🏗️ **Промышленное решение** для государственных контролирующих органов
- 📱 **Мультиплатформенность**: Веб + PWA + мобильные приложения  
- 🗺️ **Геолокационная привязка** всех операций с верификацией присутствия
- 📋 **Электронный журнал** производства работ с полной трассируемостью
- 🔍 **Система контроля качества** с автоматическим выявлением нарушений
- 💬 **Real-time коммуникация** между участниками проекта
- 📊 **Аналитика и отчетность** с интерактивными дашбордами
- 🔒 **Соответствие ФЗ-152** и требованиям информационной безопасности

## Технологический стек

### Backend
- **Django 4.2+** - Основной фреймворк и бизнес-логика
- **FastAPI 0.104+** - Высокопроизводительные микросервисы
- **PostgreSQL 15+** - Основная база данных
- **PostGIS** - Геопространственные данные
- **Redis 7+** - Кэширование и сессии
- **Celery** - Асинхронная обработка задач

### Frontend
- **HTML5/CSS3** - Семантическая разметка и стили
- **JavaScript ES6+** - Основная логика интерфейса
- **Bootstrap 5.3+** - Адаптивный дизайн
- **Chart.js 4+** - Интерактивные графики
- **Leaflet.js** - Картографические функции
- **Socket.IO** - Real-time коммуникация

### Infrastructure
- **Docker** - Контейнеризация
- **Kubernetes** - Оркестрация в продакшене
- **Nginx** - Reverse proxy
- **Prometheus + Grafana** - Мониторинг
- **ELK Stack** - Логирование

## Быстрый старт

### Требования
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- 16GB RAM (рекомендуется)

### Локальная разработка

```bash
# Клонирование репозитория
git clone https://github.com/organization/journal-system.git
cd journal-system

# Копирование конфигурации
cp .env.example .env.development

# Запуск через Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# В новом терминале - миграции
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py loaddata fixtures/initial_data.json

# Создание суперпользователя
docker-compose exec django python manage.py createsuperuser
```

### Доступ к сервисам
- **Frontend**: http://localhost/
- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8001/docs
- **Grafana**: http://localhost:3000/

## Документация

Полная документация проекта находится в папке [docs/](./docs/):

1. [📋 Описание проекта](./docs/01_project_description.md)
2. [⚙️ Техническое описание](./docs/02_technical_description.md)
3. [📂 Структура проекта](./docs/03_project_structure.md)
4. [🎯 Функциональные требования](./docs/04_functional_requirements.md)
5. [🔧 Нефункциональные требования](./docs/05_non_functional_requirements.md)
6. [📊 Структура данных](./docs/06_data_structure.md)
7. [🗄️ База данных](./docs/07_database.md)
8. [🔌 API Спецификация](./docs/08_api_specification.md)
9. [🖥️ Пользовательский интерфейс](./docs/09_user_interface.md)
10. [🚀 Установка и развертывание](./docs/10_deployment.md)
11. [🧪 Тестирование](./docs/11_testing.md)
12. [📈 Мониторинг и логирование](./docs/12_monitoring.md)
13. [🔐 Безопасность](./docs/13_security.md)
14. [💻 Разработка](./docs/14_development.md)
15. [👥 Команда проекта](./docs/15_team.md)
16. [🗓️ Roadmap](./docs/16_roadmap.md)
17. [⚠️ Риски и митигация](./docs/17_risks.md)
18. [📞 Контакты и поддержка](./docs/18_contacts.md)

## Основные функции

### Для подрядчиков
- ✅ Создание записей в электронном журнале работ
- 📸 Фотофиксация с геопривязкой
- 📄 Загрузка исполнительной документации
- 📊 Отслеживание прогресса работ

### Для контролирующих органов
- 🔍 Проведение контрольных мероприятий
- 🚨 Выявление и фиксация нарушений
- 📋 Назначение сроков устранения недостатков
- 📈 Формирование аналитических отчетов

### Для заказчиков
- 👀 Мониторинг хода выполнения работ
- 📊 Аналитические дашборды
- 📑 Автоматические отчеты
- 💬 Коммуникация с участниками

## Безопасность

- 🔐 **Многофакторная аутентификация** (2FA/MFA)
- 🌐 **Интеграция с ЕСИА** 
- 🔒 **Шифрование данных** (AES-256)
- 🛡️ **Соответствие ФЗ-152** о персональных данных
- 🔍 **Аудит всех действий** пользователей
- 🚨 **Мониторинг безопасности** 24/7

## Производительность

- ⚡ **До 10,000 одновременных пользователей**
- 🚀 **API ответы < 500ms**
- 📈 **99.9% uptime** (SLA)
- 💾 **Автоматическое масштабирование**
- 🔄 **Горизонтальное масштабирование**

## Поддержка

### Техническая поддержка
- 📧 **Email**: support@journal-system.ru
- 📞 **Телефон**: +7 (495) 123-45-67
- 💬 **Telegram**: @journal_support_bot
- 🌐 **Портал**: https://support.journal-system.ru

### Экстренная поддержка 24/7
- 🚨 **Hotline**: +7 (495) 123-45-99
- ⚡ **Время ответа**: 30 минут (критические инциденты)

## Лицензия

Проприетарная лицензия. Все права защищены.

## Команда

- **CTO**: Алексей Иванов (a.ivanov@journal-system.ru)
- **Lead Backend**: Дмитрий Волков (d.volkov@journal-system.ru)
- **Lead Frontend**: Ольга Новикова (o.novikova@journal-system.ru)
- **DevOps**: Сергей Морозов (s.morozov@journal-system.ru)

## Статус проекта

🚧 **В разработке** - MVP планируется к концу 4 недели

---

**Организация**: ООО "Цифровые Решения"  
**Сайт**: https://journal-system.ru  
**Email**: info@journal-system.ru
