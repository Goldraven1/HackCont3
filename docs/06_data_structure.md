# 6. Структура данных

## 6.1 Входные данные

### 6.1.1 Данные от пользователей

#### Записи журнала производства работ
```json
{
  "entry_id": "uuid",
  "project_id": "uuid",
  "work_type": "string",
  "work_description": "text",
  "work_volume": "decimal",
  "unit_of_measure": "string",
  "start_time": "datetime",
  "end_time": "datetime",
  "location": {
    "latitude": "decimal",
    "longitude": "decimal",
    "accuracy": "decimal",
    "verification_method": "string"
  },
  "participants": [
    {
      "user_id": "uuid",
      "role": "string",
      "organization": "string"
    }
  ],
  "materials": [
    {
      "material_id": "uuid",
      "quantity": "decimal",
      "certificate_number": "string"
    }
  ],
  "photos": ["file_ids"],
  "documents": ["file_ids"],
  "quality_control": {
    "status": "string",
    "inspector_id": "uuid",
    "comments": "text"
  }
}
```

#### Данные контроля качества
```json
{
  "control_id": "uuid",
  "entry_id": "uuid",
  "control_type": "string",
  "inspector": {
    "user_id": "uuid",
    "organization": "string",
    "position": "string"
  },
  "violations": [
    {
      "violation_code": "string",
      "description": "text",
      "severity": "string",
      "deadline": "date",
      "status": "string"
    }
  ],
  "photos": ["file_ids"],
  "documents": ["file_ids"],
  "result": "string",
  "recommendations": "text"
}
```

### 6.1.2 Справочные данные

#### Справочник предметов государственного заказа (СПГЗ)
```json
{
  "spgz_code": "string",
  "name": "string",
  "description": "text",
  "unit_of_measure": "string",
  "category": "string",
  "subcategory": "string",
  "version": "string",
  "effective_date": "date"
}
```

#### Классификатор нарушений
```json
{
  "violation_code": "string",
  "name": "string",
  "description": "text",
  "category": "string",
  "severity": "string",
  "typical_deadline": "integer",
  "regulatory_basis": "text"
}
```

#### Реестр объектов благоустройства
```json
{
  "object_id": "uuid",
  "name": "string",
  "address": "string",
  "region": "string",
  "coordinates": {
    "center": {
      "latitude": "decimal",
      "longitude": "decimal"
    },
    "boundary": "geojson_polygon"
  },
  "object_type": "string",
  "customer": "string",
  "contractor": "string",
  "project_value": "decimal",
  "start_date": "date",
  "planned_end_date": "date",
  "status": "string"
}
```

### 6.1.3 Документы и файлы

#### Структура файловых данных
```json
{
  "file_id": "uuid",
  "original_name": "string",
  "file_type": "string",
  "mime_type": "string",
  "size": "integer",
  "upload_date": "datetime",
  "uploaded_by": "uuid",
  "storage_path": "string",
  "metadata": {
    "location": {
      "latitude": "decimal",
      "longitude": "decimal"
    },
    "device_info": "string",
    "timestamp": "datetime"
  },
  "checksums": {
    "md5": "string",
    "sha256": "string"
  }
}
```

## 6.2 Выходные показатели

### 6.2.1 Аналитические данные

#### KPI по объектам
```json
{
  "object_id": "uuid",
  "period": {
    "start_date": "date",
    "end_date": "date"
  },
  "metrics": {
    "total_entries": "integer",
    "work_types_count": "integer",
    "violations_count": "integer",
    "critical_violations": "integer",
    "resolved_violations": "integer",
    "average_resolution_time": "decimal",
    "quality_score": "decimal",
    "progress_percentage": "decimal"
  },
  "participants_activity": [
    {
      "organization": "string",
      "entries_count": "integer",
      "last_activity": "datetime"
    }
  ]
}
```

#### Региональная статистика
```json
{
  "region": "string",
  "period": {
    "start_date": "date",
    "end_date": "date"
  },
  "statistics": {
    "total_objects": "integer",
    "active_objects": "integer",
    "completed_objects": "integer",
    "total_violations": "integer",
    "resolved_violations_percentage": "decimal",
    "average_project_duration": "decimal",
    "total_investment": "decimal"
  },
  "top_violations": [
    {
      "violation_code": "string",
      "count": "integer",
      "percentage": "decimal"
    }
  ]
}
```

### 6.2.2 Отчетные данные

#### Отчет по объекту
```json
{
  "report_id": "uuid",
  "object_id": "uuid",
  "report_type": "string",
  "generation_date": "datetime",
  "period": {
    "start_date": "date",
    "end_date": "date"
  },
  "summary": {
    "total_work_days": "integer",
    "completed_work_types": "integer",
    "total_violations": "integer",
    "resolved_violations": "integer",
    "quality_assessment": "string"
  },
  "work_progress": [
    {
      "work_type": "string",
      "planned_volume": "decimal",
      "completed_volume": "decimal",
      "completion_percentage": "decimal"
    }
  ],
  "violations_summary": [
    {
      "category": "string",
      "count": "integer",
      "resolved_count": "integer"
    }
  ],
  "file_attachments": ["file_ids"]
}
```

### 6.2.3 API Response форматы

#### Стандартный API Response
```json
{
  "success": "boolean",
  "data": "object|array",
  "message": "string",
  "error_code": "string",
  "timestamp": "datetime",
  "request_id": "uuid",
  "pagination": {
    "page": "integer",
    "per_page": "integer",
    "total": "integer",
    "total_pages": "integer"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object",
    "field_errors": {
      "field_name": ["error_messages"]
    }
  },
  "timestamp": "datetime",
  "request_id": "uuid"
}
```

## 6.3 Валидация данных

### 6.3.1 Правила валидации

#### Геолокационные данные
- **Координаты**: Должны находиться в пределах границ объекта (±50 метров)
- **Точность GPS**: Не менее 10 метров для критических операций
- **Временные метки**: Не старше 5 минут от времени создания записи

#### Документы и файлы
- **Размер файлов**: Максимум 100MB для документов, 50MB для изображений
- **Форматы**: PDF, DOC, DOCX для документов; JPG, PNG для изображений
- **Вирусная проверка**: Обязательная проверка всех загружаемых файлов

#### Бизнес-правила
- **Временные рамки**: Записи можно создавать только в рабочее время (7:00-22:00)
- **Последовательность работ**: Контроль соблюдения технологической последовательности
- **Ролевые ограничения**: Пользователи могут создавать записи только в рамках своих полномочий

### 6.3.2 Контроль целостности

#### Ссылочная целостность
- Все внешние ключи должны ссылаться на существующие записи
- Каскадное удаление для зависимых данных
- Проверка существования объектов при создании записей

#### Бизнес-логика
- Один пользователь не может находиться на двух объектах одновременно
- Нельзя закрыть объект при наличии незакрытых нарушений
- Контроль уникальности номеров документов

---

*Структура данных обеспечивает полную трассируемость и контроль качества всех процессов в промышленной системе*
