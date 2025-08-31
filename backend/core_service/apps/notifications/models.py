from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class NotificationType(models.Model):
    """Модель типа уведомления"""
    
    PRIORITY_LEVELS = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название типа', max_length=200)
    code = models.CharField('Код типа', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    
    # Настройки
    priority = models.CharField('Приоритет', max_length=20, choices=PRIORITY_LEVELS, default='medium')
    icon = models.CharField('Иконка', max_length=50, blank=True)
    color = models.CharField('Цвет', max_length=20, blank=True)
    
    # Шаблоны
    title_template = models.CharField('Шаблон заголовка', max_length=500)
    message_template = models.TextField('Шаблон сообщения')
    
    # Настройки доставки
    email_enabled = models.BooleanField('Отправлять на email', default=True)
    sms_enabled = models.BooleanField('Отправлять SMS', default=False)
    push_enabled = models.BooleanField('Push-уведомления', default=True)
    
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'notification_types'
        verbose_name = 'Тип уведомления'
        verbose_name_plural = 'Типы уведомлений'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """Модель уведомления"""
    
    DELIVERY_STATUSES = [
        ('pending', 'Ожидает отправки'),
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('read', 'Прочитано'),
        ('failed', 'Ошибка отправки'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Тип уведомления'
    )
    
    # Получатели
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name='Получатель'
    )
    
    # Содержание
    title = models.CharField('Заголовок', max_length=500)
    message = models.TextField('Сообщение')
    
    # Связанные объекты
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Проект',
        null=True,
        blank=True
    )
    journal_entry = models.ForeignKey(
        'journal.JournalEntry',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Запись журнала',
        null=True,
        blank=True
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Документ',
        null=True,
        blank=True
    )
    
    # Метаданные
    data = models.JSONField('Дополнительные данные', default=dict, blank=True)
    
    # Статусы доставки
    email_status = models.CharField('Статус email', max_length=20, choices=DELIVERY_STATUSES, default='pending')
    sms_status = models.CharField('Статус SMS', max_length=20, choices=DELIVERY_STATUSES, default='pending')
    push_status = models.CharField('Статус push', max_length=20, choices=DELIVERY_STATUSES, default='pending')
    
    # Времена
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    sent_at = models.DateTimeField('Отправлено', null=True, blank=True)
    read_at = models.DateTimeField('Прочитано', null=True, blank=True)
    
    # Настройки
    is_urgent = models.BooleanField('Срочное', default=False)
    expires_at = models.DateTimeField('Истекает', null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_urgent']),
        ]
    
    def __str__(self):
        return f"{self.title} → {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    @property
    def is_read(self):
        """Проверка прочтения"""
        return self.read_at is not None
    
    @property
    def is_expired(self):
        """Проверка истечения срока"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class NotificationRule(models.Model):
    """Модель правила уведомлений"""
    
    TRIGGER_EVENTS = [
        ('journal_entry_created', 'Создание записи журнала'),
        ('journal_entry_approved', 'Утверждение записи журнала'),
        ('journal_entry_rejected', 'Отклонение записи журнала'),
        ('document_uploaded', 'Загрузка документа'),
        ('document_approved', 'Утверждение документа'),
        ('project_deadline_near', 'Приближение срока проекта'),
        ('project_overdue', 'Просрочка проекта'),
        ('quality_issue', 'Проблемы с качеством'),
        ('safety_incident', 'Происшествие по безопасности'),
        ('delay_reported', 'Сообщение о задержке'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название правила', max_length=200)
    description = models.TextField('Описание', blank=True)
    
    # Триггер
    trigger_event = models.CharField('Событие-триггер', max_length=50, choices=TRIGGER_EVENTS)
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name='rules',
        verbose_name='Тип уведомления'
    )
    
    # Условия
    conditions = models.JSONField('Условия', default=dict, blank=True)
    
    # Получатели
    recipient_roles = models.JSONField('Роли получателей', default=list, blank=True)
    specific_users = models.ManyToManyField(
        User,
        related_name='notification_rules',
        verbose_name='Конкретные пользователи',
        blank=True
    )
    
    # Настройки
    is_active = models.BooleanField('Активно', default=True)
    delay_minutes = models.PositiveIntegerField('Задержка (минуты)', default=0)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_notification_rules',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        db_table = 'notification_rules'
        verbose_name = 'Правило уведомлений'
        verbose_name_plural = 'Правила уведомлений'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_event_display()})"


class NotificationPreference(models.Model):
    """Модель настроек уведомлений пользователя"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Пользователь'
    )
    
    # Общие настройки
    email_notifications = models.BooleanField('Email уведомления', default=True)
    sms_notifications = models.BooleanField('SMS уведомления', default=False)
    push_notifications = models.BooleanField('Push уведомления', default=True)
    
    # Время доставки
    quiet_hours_start = models.TimeField('Начало тихих часов', null=True, blank=True)
    quiet_hours_end = models.TimeField('Конец тихих часов', null=True, blank=True)
    
    # Настройки по типам
    notification_settings = models.JSONField('Настройки по типам', default=dict, blank=True)
    
    # Группировка
    digest_enabled = models.BooleanField('Дайджест уведомлений', default=False)
    digest_frequency = models.CharField(
        'Частота дайджеста',
        max_length=20,
        choices=[
            ('hourly', 'Каждый час'),
            ('daily', 'Ежедневно'),
            ('weekly', 'Еженедельно'),
        ],
        default='daily'
    )
    
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'
    
    def __str__(self):
        return f"Настройки уведомлений - {self.user.get_full_name()}"
    
    def is_in_quiet_hours(self):
        """Проверка тихих часов"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        return self.quiet_hours_start <= now <= self.quiet_hours_end
    
    def should_send_notification(self, notification_type, delivery_method):
        """Проверка необходимости отправки уведомления"""
        # Проверяем общие настройки
        if delivery_method == 'email' and not self.email_notifications:
            return False
        elif delivery_method == 'sms' and not self.sms_notifications:
            return False
        elif delivery_method == 'push' and not self.push_notifications:
            return False
        
        # Проверяем тихие часы
        if self.is_in_quiet_hours():
            return False
        
        # Проверяем настройки по типам
        type_settings = self.notification_settings.get(notification_type.code, {})
        if not type_settings.get(f'{delivery_method}_enabled', True):
            return False
        
        return True


class NotificationDeliveryLog(models.Model):
    """Модель лога доставки уведомлений"""
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('webhook', 'Webhook'),
    ]
    
    DELIVERY_STATUSES = [
        ('success', 'Успешно'),
        ('failed', 'Неудача'),
        ('retry', 'Повтор'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs',
        verbose_name='Уведомление'
    )
    
    delivery_method = models.CharField('Способ доставки', max_length=20, choices=DELIVERY_METHODS)
    status = models.CharField('Статус', max_length=20, choices=DELIVERY_STATUSES)
    
    # Детали доставки
    recipient_address = models.CharField('Адрес получателя', max_length=255)  # email, phone, device_id
    provider = models.CharField('Провайдер', max_length=100, blank=True)
    external_id = models.CharField('Внешний ID', max_length=255, blank=True)
    
    # Результат
    response_code = models.CharField('Код ответа', max_length=20, blank=True)
    response_message = models.TextField('Сообщение ответа', blank=True)
    error_details = models.TextField('Детали ошибки', blank=True)
    
    # Время
    attempt_at = models.DateTimeField('Время попытки', auto_now_add=True)
    delivered_at = models.DateTimeField('Время доставки', null=True, blank=True)
    
    # Метрики
    processing_time_ms = models.PositiveIntegerField('Время обработки (мс)', null=True, blank=True)
    
    class Meta:
        db_table = 'notification_delivery_logs'
        verbose_name = 'Лог доставки уведомления'
        verbose_name_plural = 'Логи доставки уведомлений'
        ordering = ['-attempt_at']
        indexes = [
            models.Index(fields=['notification', 'delivery_method']),
            models.Index(fields=['status']),
            models.Index(fields=['attempt_at']),
        ]
    
    def __str__(self):
        return f"{self.delivery_method}: {self.status} - {self.notification.title[:50]}"
