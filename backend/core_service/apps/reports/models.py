from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ReportTemplate(models.Model):
    """Модель шаблона отчета"""
    
    REPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
        ('json', 'JSON'),
    ]
    
    REPORT_CATEGORIES = [
        ('project', 'Отчеты по проектам'),
        ('journal', 'Отчеты по журналу'),
        ('quality', 'Отчеты по качеству'),
        ('safety', 'Отчеты по безопасности'),
        ('finance', 'Финансовые отчеты'),
        ('analytics', 'Аналитические отчеты'),
        ('compliance', 'Отчеты соответствия'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название шаблона', max_length=200)
    description = models.TextField('Описание', blank=True)
    category = models.CharField('Категория', max_length=20, choices=REPORT_CATEGORIES)
    
    # Настройки шаблона
    template_file_id = models.CharField('ID файла шаблона', max_length=100, blank=True)
    query_template = models.TextField('Шаблон запроса', blank=True)
    parameters = models.JSONField('Параметры', default=list, blank=True)
    
    # Форматы вывода
    supported_formats = models.JSONField('Поддерживаемые форматы', default=list, blank=True)
    default_format = models.CharField('Формат по умолчанию', max_length=10, choices=REPORT_FORMATS, default='pdf')
    
    # Настройки доступа
    is_public = models.BooleanField('Публичный', default=False)
    allowed_roles = models.JSONField('Разрешенные роли', default=list, blank=True)
    
    # Автоматизация
    is_scheduled = models.BooleanField('Запланированный', default=False)
    schedule_cron = models.CharField('Расписание (cron)', max_length=100, blank=True)
    auto_recipients = models.ManyToManyField(
        User,
        related_name='auto_reports',
        verbose_name='Автоматические получатели',
        blank=True
    )
    
    # Метаданные
    is_active = models.BooleanField('Активен', default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
        verbose_name = 'Шаблон отчета'
        verbose_name_plural = 'Шаблоны отчетов'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Report(models.Model):
    """Модель сгенерированного отчета"""
    
    REPORT_STATUSES = [
        ('pending', 'Ожидает'),
        ('generating', 'Генерируется'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Шаблон'
    )
    
    # Параметры генерации
    title = models.CharField('Заголовок отчета', max_length=500)
    parameters = models.JSONField('Параметры', default=dict, blank=True)
    format = models.CharField('Формат', max_length=10, choices=ReportTemplate.REPORT_FORMATS)
    
    # Период отчета
    date_from = models.DateField('Дата начала', null=True, blank=True)
    date_to = models.DateField('Дата окончания', null=True, blank=True)
    
    # Фильтры
    projects = models.ManyToManyField(
        'projects.Project',
        related_name='reports',
        verbose_name='Проекты',
        blank=True
    )
    organizations = models.ManyToManyField(
        'users.Organization',
        related_name='reports',
        verbose_name='Организации',
        blank=True
    )
    
    # Статус и результат
    status = models.CharField('Статус', max_length=20, choices=REPORT_STATUSES, default='pending')
    file_id = models.CharField('ID файла результата', max_length=100, blank=True)
    filename = models.CharField('Имя файла', max_length=255, blank=True)
    file_size = models.PositiveIntegerField('Размер файла (байты)', null=True, blank=True)
    
    # Метрики
    records_count = models.PositiveIntegerField('Количество записей', null=True, blank=True)
    generation_time_seconds = models.PositiveIntegerField('Время генерации (сек)', null=True, blank=True)
    
    # Ошибки
    error_message = models.TextField('Сообщение об ошибке', blank=True)
    error_details = models.TextField('Детали ошибки', blank=True)
    
    # Автор и время
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requested_reports',
        verbose_name='Запросил'
    )
    requested_at = models.DateTimeField('Запрошен', auto_now_add=True)
    started_at = models.DateTimeField('Начат', null=True, blank=True)
    completed_at = models.DateTimeField('Завершен', null=True, blank=True)
    
    # Доступ
    is_public = models.BooleanField('Публичный', default=False)
    expires_at = models.DateTimeField('Истекает', null=True, blank=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['template', 'status']),
            models.Index(fields=['requested_by']),
            models.Index(fields=['date_from', 'date_to']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.requested_at.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def is_expired(self):
        """Проверка истечения срока"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_generating(self):
        """Отметить как генерирующийся"""
        self.status = 'generating'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_as_completed(self, file_id, filename, file_size, records_count=None):
        """Отметить как завершенный"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.file_id = file_id
        self.filename = filename
        self.file_size = file_size
        self.records_count = records_count
        
        if self.started_at:
            self.generation_time_seconds = (self.completed_at - self.started_at).total_seconds()
        
        self.save(update_fields=[
            'status', 'completed_at', 'file_id', 'filename', 'file_size',
            'records_count', 'generation_time_seconds'
        ])
    
    def mark_as_failed(self, error_message, error_details=None):
        """Отметить как неудачный"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.error_details = error_details or ''
        
        self.save(update_fields=['status', 'completed_at', 'error_message', 'error_details'])


class ReportSchedule(models.Model):
    """Модель расписания автоматических отчетов"""
    
    SCHEDULE_FREQUENCIES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('quarterly', 'Ежеквартально'),
        ('yearly', 'Ежегодно'),
        ('custom', 'Пользовательское'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Шаблон'
    )
    
    name = models.CharField('Название расписания', max_length=200)
    description = models.TextField('Описание', blank=True)
    
    # Настройки расписания
    frequency = models.CharField('Частота', max_length=20, choices=SCHEDULE_FREQUENCIES)
    cron_expression = models.CharField('Cron выражение', max_length=100, blank=True)
    
    # Время выполнения
    time_of_day = models.TimeField('Время суток', default='09:00')
    timezone = models.CharField('Часовой пояс', max_length=50, default='Europe/Moscow')
    
    # Параметры отчета
    parameters = models.JSONField('Параметры', default=dict, blank=True)
    format = models.CharField('Формат', max_length=10, choices=ReportTemplate.REPORT_FORMATS, default='pdf')
    
    # Получатели
    recipients = models.ManyToManyField(
        User,
        related_name='scheduled_reports',
        verbose_name='Получатели'
    )
    
    # Статус
    is_active = models.BooleanField('Активно', default=True)
    last_run_at = models.DateTimeField('Последний запуск', null=True, blank=True)
    next_run_at = models.DateTimeField('Следующий запуск', null=True, blank=True)
    
    # Метаданные
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        db_table = 'report_schedules'
        verbose_name = 'Расписание отчетов'
        verbose_name_plural = 'Расписания отчетов'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class ReportAccess(models.Model):
    """Модель доступа к отчету"""
    
    ACCESS_TYPES = [
        ('view', 'Просмотр'),
        ('download', 'Скачивание'),
        ('share', 'Совместное использование'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='access_permissions',
        verbose_name='Отчет'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report_permissions',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    organization = models.ForeignKey(
        'users.Organization',
        on_delete=models.CASCADE,
        related_name='report_permissions',
        verbose_name='Организация',
        null=True,
        blank=True
    )
    
    access_type = models.CharField('Тип доступа', max_length=20, choices=ACCESS_TYPES, default='view')
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='granted_report_permissions',
        verbose_name='Предоставил доступ'
    )
    granted_at = models.DateTimeField('Предоставлен', auto_now_add=True)
    
    # Ограничения по времени
    valid_until = models.DateTimeField('Действителен до', null=True, blank=True)
    
    class Meta:
        db_table = 'report_access'
        verbose_name = 'Доступ к отчету'
        verbose_name_plural = 'Доступы к отчетам'
        unique_together = [
            ['report', 'user', 'access_type'],
            ['report', 'organization', 'access_type'],
        ]
    
    def __str__(self):
        target = self.user.get_full_name() if self.user else self.organization.name
        return f"{self.report.title} - {target} ({self.get_access_type_display()})"
    
    @property
    def is_valid(self):
        """Проверка действительности доступа"""
        if self.valid_until:
            return timezone.now() <= self.valid_until
        return True


class ReportMetrics(models.Model):
    """Модель метрик использования отчетов"""
    
    ACTION_TYPES = [
        ('view', 'Просмотр'),
        ('download', 'Скачивание'),
        ('share', 'Совместное использование'),
        ('export', 'Экспорт'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name='Отчет'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report_actions',
        verbose_name='Пользователь'
    )
    
    action_type = models.CharField('Тип действия', max_length=20, choices=ACTION_TYPES)
    ip_address = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    # Метаданные действия
    duration_seconds = models.PositiveIntegerField('Длительность (сек)', null=True, blank=True)
    file_format = models.CharField('Формат файла', max_length=10, blank=True)
    
    timestamp = models.DateTimeField('Время', auto_now_add=True)
    
    class Meta:
        db_table = 'report_metrics'
        verbose_name = 'Метрика отчета'
        verbose_name_plural = 'Метрики отчетов'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['report', 'action_type']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()}: {self.report.title} - {self.user.get_full_name()}"
