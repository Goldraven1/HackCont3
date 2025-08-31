# Django Core Service

Основной сервис электронного журнала производства работ на Django.

## Установка

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
```

## Приложения

- `users` - Управление пользователями и организациями
- `projects` - Проекты и объекты благоустройства
- `journal` - Журнал производства работ
- `documents` - Документооборот
- `notifications` - Система уведомлений
- `reports` - Отчеты и аналитика

## API

Документация API доступна по адресу: `/api/docs/`

## Тесты

```bash
python manage.py test
pytest
```
