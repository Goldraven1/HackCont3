# 8. API Спецификация

## 8.1 Endpoints

### 8.1.1 Data Processing API (FastAPI)

#### Файловый сервис
**Base URL**: `https://api.journal-system.ru/files/v1`

##### Загрузка файлов
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: binary (required) - Загружаемый файл
- object_id: uuid (required) - ID объекта
- entry_id: uuid (optional) - ID записи журнала
- file_type: string (required) - Тип файла (photo, document, certificate)
- location: object (optional) - Координаты съемки

Response 201:
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "original_name": "string",
    "file_type": "string",
    "size": 1024,
    "upload_date": "2024-01-01T10:00:00Z",
    "download_url": "string",
    "thumbnail_url": "string"
  }
}
```

##### Получение файла
```http
GET /files/{file_id}

Parameters:
- file_id: uuid (required)
- download: boolean (optional) - Принудительная загрузка

Response 200:
- Binary content или редирект на CDN URL
```

##### Массовая загрузка
```http
POST /bulk-upload
Content-Type: multipart/form-data

Parameters:
- files[]: binary[] (required) - Массив файлов
- metadata: json (required) - Метаданные для каждого файла

Response 201:
{
  "success": true,
  "data": {
    "uploaded_files": [
      {
        "file_id": "uuid",
        "original_name": "string",
        "status": "success|error",
        "error_message": "string"
      }
    ],
    "summary": {
      "total": 5,
      "successful": 4,
      "failed": 1
    }
  }
}
```

#### GIS Сервис
**Base URL**: `https://api.journal-system.ru/gis/v1`

##### Валидация местоположения
```http
POST /validate-location
Content-Type: application/json

{
  "object_id": "uuid",
  "latitude": 55.7558,
  "longitude": 37.6176,
  "accuracy": 5.0
}

Response 200:
{
  "success": true,
  "data": {
    "is_valid": true,
    "distance_to_boundary": 12.5,
    "within_work_zone": true,
    "alternative_verification": {
      "qr_code_available": true,
      "nfc_available": false
    }
  }
}
```

##### Получение карты объекта
```http
GET /objects/{object_id}/map

Parameters:
- zoom: integer (optional, default: 15)
- format: string (optional, default: "geojson")

Response 200:
{
  "success": true,
  "data": {
    "object_boundary": "geojson_polygon",
    "work_zones": ["geojson_polygon"],
    "access_points": ["geojson_point"],
    "nearby_objects": [
      {
        "object_id": "uuid",
        "name": "string",
        "distance": 150.5
      }
    ]
  }
}
```

### 8.1.2 Analytics API (Django REST)

#### Основной API
**Base URL**: `https://api.journal-system.ru/api/v1`

##### Журнал работ

###### Создание записи
```http
POST /journal/entries/
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "project_id": "uuid",
  "work_type": "foundation",
  "work_description": "Устройство фундамента",
  "work_volume": 150.5,
  "unit_of_measure": "м³",
  "location": {
    "latitude": 55.7558,
    "longitude": 37.6176,
    "accuracy": 3.5
  },
  "participants": [
    {
      "user_id": "uuid",
      "role": "executor"
    }
  ],
  "materials": [
    {
      "material_id": "uuid",
      "quantity": 100.0,
      "certificate_number": "CERT-2024-001"
    }
  ],
  "photos": ["file_id_1", "file_id_2"],
  "documents": ["file_id_3"]
}

Response 201:
{
  "success": true,
  "data": {
    "entry_id": "uuid",
    "entry_number": "2024-001-001",
    "created_at": "2024-01-01T10:00:00Z",
    "status": "active",
    "verification_status": "verified"
  }
}
```

###### Получение списка записей
```http
GET /journal/entries/

Parameters:
- project_id: uuid (optional)
- work_type: string (optional)
- date_from: date (optional)
- date_to: date (optional)
- status: string (optional)
- page: integer (optional, default: 1)
- per_page: integer (optional, default: 20, max: 100)

Response 200:
{
  "success": true,
  "data": {
    "entries": [
      {
        "entry_id": "uuid",
        "entry_number": "string",
        "work_type": "string",
        "work_description": "string",
        "created_at": "datetime",
        "status": "string",
        "author": {
          "user_id": "uuid",
          "name": "string",
          "organization": "string"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8
    }
  }
}
```

##### Контроль качества

###### Создание нарушения
```http
POST /quality-control/violations/
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "entry_id": "uuid",
  "violation_code": "VIO-001",
  "description": "Нарушение технологии укладки",
  "severity": "high",
  "deadline": "2024-01-15",
  "photos": ["file_id_1"],
  "location": {
    "latitude": 55.7558,
    "longitude": 37.6176
  }
}

Response 201:
{
  "success": true,
  "data": {
    "violation_id": "uuid",
    "violation_number": "V-2024-001",
    "status": "open",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

##### Отчеты и аналитика

###### Генерация отчета по объекту
```http
POST /reports/object/{object_id}/
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "report_type": "progress",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "format": "pdf",
  "include_photos": true
}

Response 202:
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "processing",
    "estimated_completion": "2024-01-01T10:05:00Z"
  }
}
```

###### Получение статуса генерации отчета
```http
GET /reports/tasks/{task_id}/

Response 200:
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "completed",
    "result": {
      "download_url": "string",
      "file_size": 2048576,
      "expires_at": "2024-01-02T10:00:00Z"
    }
  }
}
```

##### KPI и метрики

###### Получение KPI объекта
```http
GET /analytics/objects/{object_id}/kpi/

Parameters:
- period: string (optional: "week", "month", "quarter", "year")
- date_from: date (optional)
- date_to: date (optional)

Response 200:
{
  "success": true,
  "data": {
    "object_id": "uuid",
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "metrics": {
      "total_entries": 156,
      "work_types_count": 12,
      "violations_count": 8,
      "critical_violations": 2,
      "resolved_violations": 6,
      "average_resolution_time": 3.5,
      "quality_score": 87.5,
      "progress_percentage": 65.3
    },
    "trends": {
      "entries_trend": 15.2,
      "quality_trend": -5.1,
      "resolution_time_trend": -12.3
    }
  }
}
```

## 8.2 Аутентификация

### 8.2.1 JWT Authentication

#### Получение токена
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "device_info": {
    "device_type": "web|mobile",
    "user_agent": "string",
    "ip_address": "string"
  }
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "jwt_token",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "user_id": "uuid",
      "username": "string",
      "email": "string",
      "role": "string",
      "organization": "string",
      "permissions": ["perm1", "perm2"]
    }
  }
}
```

#### Обновление токена
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh_token": "jwt_token"
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token",
    "expires_in": 3600
  }
}
```

### 8.2.2 ЕСИА Integration

#### Инициация авторизации через ЕСИА
```http
GET /auth/esia/authorize/

Parameters:
- redirect_uri: string (required)
- state: string (optional)

Response 302:
- Редирект на ЕСИА с необходимыми параметрами
```

#### Обработка callback от ЕСИА
```http
POST /auth/esia/callback/
Content-Type: application/json

{
  "code": "authorization_code",
  "state": "string"
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "refresh_token": "jwt_token",
    "user": {
      "esia_id": "string",
      "snils": "string",
      "inn": "string",
      "first_name": "string",
      "last_name": "string",
      "middle_name": "string"
    }
  }
}
```

## 8.3 Коды ошибок

### Стандартные HTTP коды
- **200 OK** - Успешный запрос
- **201 Created** - Ресурс создан
- **202 Accepted** - Запрос принят к обработке
- **400 Bad Request** - Ошибка в запросе
- **401 Unauthorized** - Требуется аутентификация
- **403 Forbidden** - Недостаточно прав
- **404 Not Found** - Ресурс не найден
- **409 Conflict** - Конфликт данных
- **422 Unprocessable Entity** - Ошибка валидации
- **429 Too Many Requests** - Превышен лимит запросов
- **500 Internal Server Error** - Внутренняя ошибка сервера

### Кастомные коды ошибок
```json
{
  "LOCATION_VALIDATION_FAILED": {
    "code": "LOC_001",
    "message": "Пользователь находится вне границ объекта",
    "http_status": 422
  },
  "GPS_ACCURACY_INSUFFICIENT": {
    "code": "LOC_002", 
    "message": "Недостаточная точность GPS для данной операции",
    "http_status": 422
  },
  "DUPLICATE_ENTRY": {
    "code": "ENT_001",
    "message": "Запись с такими параметрами уже существует",
    "http_status": 409
  },
  "INVALID_WORK_SEQUENCE": {
    "code": "ENT_002",
    "message": "Нарушена технологическая последовательность работ",
    "http_status": 422
  },
  "FILE_TOO_LARGE": {
    "code": "FILE_001",
    "message": "Размер файла превышает допустимый лимит",
    "http_status": 413
  },
  "UNSUPPORTED_FILE_TYPE": {
    "code": "FILE_002",
    "message": "Неподдерживаемый тип файла",
    "http_status": 415
  }
}
```

## 8.4 Rate Limiting

### Лимиты по типам запросов
- **Аутентификация**: 5 запросов в минуту
- **Загрузка файлов**: 10 файлов в минуту
- **API запросы**: 1000 запросов в час
- **Генерация отчетов**: 5 отчетов в час
- **Геолокационные запросы**: 100 запросов в минуту

### Headers для Rate Limiting
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## 8.5 Webhooks

### Настройка webhook'ов
```http
POST /webhooks/
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "url": "https://external-system.com/webhook",
  "events": ["entry.created", "violation.detected"],
  "secret": "webhook_secret",
  "active": true
}
```

### События для webhook'ов
- **entry.created** - Создана новая запись
- **entry.updated** - Обновлена запись
- **violation.detected** - Выявлено нарушение
- **violation.resolved** - Устранено нарушение
- **report.generated** - Сгенерирован отчет
- **user.login** - Вход пользователя в систему

---

*API спецификация обеспечивает полную интеграцию с внешними системами и соответствует промышленным стандартам*
