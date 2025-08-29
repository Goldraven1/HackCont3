# 10. Установка и развертывание

## 10.1 Требования к окружению

### 10.1.1 Системные требования

#### Минимальные требования для разработки
**Локальная машина разработчика**:
- **OS**: Windows 10/11, macOS 10.15+, Linux Ubuntu 20.04+
- **RAM**: 16GB (рекомендуется 32GB)
- **CPU**: 4 ядра (Intel Core i5 или AMD Ryzen 5)
- **Storage**: 100GB свободного места (SSD рекомендуется)
- **Network**: Стабильное интернет-соединение

#### Продакшн требования
**Web серверы** (каждый экземпляр):
- **OS**: Ubuntu Server 22.04 LTS
- **CPU**: 8 ядер (Intel Xeon или AMD EPYC)
- **RAM**: 32GB
- **Storage**: 500GB NVMe SSD
- **Network**: 10Gbps с резервированием

**База данных сервер**:
- **OS**: Ubuntu Server 22.04 LTS
- **CPU**: 16 ядер
- **RAM**: 64GB (с возможностью расширения до 128GB)
- **Storage**: 2TB NVMe SSD (RAID 10)
- **Network**: 10Gbps с резервированием

### 10.1.2 Программное обеспечение

#### Обязательные компоненты
```bash
# System packages
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- curl, wget
- openssl

# For development
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ client tools
- Redis CLI tools
```

#### Рекомендуемые инструменты разработки
- **IDE**: VS Code, PyCharm Professional, WebStorm
- **Database GUI**: pgAdmin, DBeaver
- **API Testing**: Postman, Insomnia
- **Git GUI**: GitKraken, SourceTree

## 10.2 Локальная разработка

### 10.2.1 Первоначальная настройка

#### Клонирование репозитория
```bash
# Клонирование основного репозитория
git clone https://github.com/organization/journal-system.git
cd journal-system

# Инициализация submodules (если используются)
git submodule update --init --recursive
```

#### Настройка environment переменных
```bash
# Копирование примера конфигурации
cp .env.example .env.development

# Редактирование конфигурации
nano .env.development
```

**Пример .env.development**:
```bash
# Database
DATABASE_URL=postgresql://journal_user:journal_pass@localhost:5432/journal_db
REDIS_URL=redis://localhost:6379/0

# Django settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# FastAPI settings
FASTAPI_ENV=development
FILE_STORAGE_PATH=/app/storage
MAX_FILE_SIZE=104857600

# External services
MAPBOX_ACCESS_TOKEN=your-mapbox-token
ESIA_CLIENT_ID=your-esia-client-id
ESIA_CLIENT_SECRET=your-esia-client-secret

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRE_HOURS=24
```

### 10.2.2 Docker развертывание для разработки

#### Запуск через Docker Compose
```bash
# Сборка и запуск всех сервисов
docker-compose -f docker-compose.dev.yml up --build

# Запуск в фоновом режиме
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

**docker-compose.dev.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: journal_db
      POSTGRES_USER: journal_user
      POSTGRES_PASSWORD: journal_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data/sql:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  django:
    build:
      context: ./backend/core_service
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend/core_service:/app
      - media_files:/app/media
    environment:
      - DATABASE_URL=postgresql://journal_user:journal_pass@postgres:5432/journal_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    command: python manage.py runserver 0.0.0.0:8000

  fastapi_files:
    build:
      context: ./backend/file_service
      dockerfile: Dockerfile.dev
    ports:
      - "8001:8001"
    volumes:
      - ./backend/file_service:/app
      - file_storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://journal_user:journal_pass@postgres:5432/journal_db
    depends_on:
      - postgres
    command: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

  fastapi_gis:
    build:
      context: ./backend/gis_service
      dockerfile: Dockerfile.dev
    ports:
      - "8002:8002"
    volumes:
      - ./backend/gis_service:/app
    environment:
      - DATABASE_URL=postgresql://journal_user:journal_pass@postgres:5432/journal_db
    depends_on:
      - postgres
    command: uvicorn main:app --host 0.0.0.0 --port 8002 --reload

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./infrastructure/nginx/dev.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - django
      - fastapi_files
      - fastapi_gis

volumes:
  postgres_data:
  redis_data:
  media_files:
  file_storage:
```

### 10.2.3 Настройка базы данных

#### Выполнение миграций Django
```bash
# Создание миграций
docker-compose exec django python manage.py makemigrations

# Применение миграций
docker-compose exec django python manage.py migrate

# Создание суперпользователя
docker-compose exec django python manage.py createsuperuser

# Загрузка начальных данных
docker-compose exec django python manage.py loaddata fixtures/initial_data.json
```

#### Настройка PostGIS
```bash
# Подключение к PostgreSQL
docker-compose exec postgres psql -U journal_user -d journal_db

# Создание PostGIS расширения
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Проверка установки
SELECT PostGIS_Version();
```

### 10.2.4 Проверка установки

#### Health check endpoints
```bash
# Django backend
curl http://localhost:8000/api/health/

# FastAPI файловый сервис
curl http://localhost:8001/health/

# FastAPI GIS сервис
curl http://localhost:8002/health/

# Frontend
curl http://localhost/
```

**Ожидаемые ответы**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "storage": "available"
  }
}
```

## 10.3 Продакшн развертывание

### 10.3.1 Kubernetes кластер

#### Структура манифестов
```
infrastructure/kubernetes/
├── namespace.yaml
├── configmaps/
│   ├── django-config.yaml
│   ├── fastapi-config.yaml
│   └── nginx-config.yaml
├── secrets/
│   ├── database-secret.yaml
│   ├── app-secret.yaml
│   └── tls-secret.yaml
├── deployments/
│   ├── django-deployment.yaml
│   ├── fastapi-files-deployment.yaml
│   ├── fastapi-gis-deployment.yaml
│   └── nginx-deployment.yaml
├── services/
│   ├── django-service.yaml
│   ├── fastapi-files-service.yaml
│   ├── fastapi-gis-service.yaml
│   └── nginx-service.yaml
├── ingress/
│   └── main-ingress.yaml
├── persistentvolumes/
│   ├── media-pv.yaml
│   └── storage-pv.yaml
└── hpa/
    ├── django-hpa.yaml
    └── fastapi-hpa.yaml
```

#### Создание namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: journal-system
  labels:
    name: journal-system
    environment: production
```

#### Django deployment
```yaml
# deployments/django-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: journal-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
      - name: django
        image: registry.company.com/journal-system/django:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 10.3.2 Database setup

#### PostgreSQL с высокой доступностью
```yaml
# Использование PostgreSQL Operator или Helm chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --set auth.postgresPassword=secretpassword \
  --set auth.database=journal_db \
  --set primary.persistence.size=100Gi \
  --set readReplicas.replicaCount=2 \
  --set metrics.enabled=true
```

#### Redis кластер
```yaml
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis \
  --set architecture=replication \
  --set auth.password=secretpassword \
  --set replica.replicaCount=2 \
  --set metrics.enabled=true
```

### 10.3.3 Мониторинг и логирование

#### Prometheus + Grafana
```bash
# Установка Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

#### ELK Stack для логов
```bash
# Elasticsearch
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace

# Kibana
helm install kibana elastic/kibana \
  --namespace logging

# Filebeat для сбора логов
helm install filebeat elastic/filebeat \
  --namespace logging
```

### 10.3.4 CI/CD Pipeline

#### GitHub Actions workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/core_service/requirements.txt
    
    - name: Run tests
      run: |
        cd backend/core_service
        python manage.py test
    
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r backend/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t ${{ secrets.REGISTRY }}/django:${{ github.sha }} backend/core_service/
        docker build -t ${{ secrets.REGISTRY }}/fastapi-files:${{ github.sha }} backend/file_service/
        docker build -t ${{ secrets.REGISTRY }}/fastapi-gis:${{ github.sha }} backend/gis_service/
    
    - name: Push to registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
        docker push ${{ secrets.REGISTRY }}/django:${{ github.sha }}
        docker push ${{ secrets.REGISTRY }}/fastapi-files:${{ github.sha }}
        docker push ${{ secrets.REGISTRY }}/fastapi-gis:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/django-app django=${{ secrets.REGISTRY }}/django:${{ github.sha }} -n journal-system
        kubectl set image deployment/fastapi-files-app fastapi-files=${{ secrets.REGISTRY }}/fastapi-files:${{ github.sha }} -n journal-system
        kubectl set image deployment/fastapi-gis-app fastapi-gis=${{ secrets.REGISTRY }}/fastapi-gis:${{ github.sha }} -n journal-system
```

### 10.3.5 Backup стратегия

#### Автоматические backup'ы
```bash
#!/bin/bash
# scripts/backup.sh

# Database backup
kubectl exec -n journal-system deployment/postgresql -- pg_dump -U journal_user journal_db > backup_$(date +%Y%m%d_%H%M%S).sql

# File storage backup
kubectl exec -n journal-system deployment/django-app -- tar -czf /tmp/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/media

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://journal-backups/database/
aws s3 cp media_backup_$(date +%Y%m%d_%H%M%S).tar.gz s3://journal-backups/media/
```

#### Cron job для backup'ов
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: journal-system
spec:
  schedule: "0 2 * * *"  # Каждый день в 2:00
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgresql -U journal_user journal_db > /backup/backup_$(date +%Y%m%d_%H%M%S).sql
              aws s3 cp /backup/backup_$(date +%Y%m%d_%H%M%S).sql s3://journal-backups/database/
          restartPolicy: OnFailure
```

---

*Документация по установке и развертыванию обеспечивает надежное развертывание промышленного решения в production окружении*
