from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Organization(models.Model):
    """Модель организации"""
    
    ORGANIZATION_TYPES = [
        ('contractor', 'Подрядчик'),
        ('supervisor', 'Надзорный орган'),
        ('customer', 'Заказчик'),
        ('government', 'Государственный орган'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название', max_length=500)
    code = models.CharField(
        'Код организации',
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Только заглавные буквы и цифры')]
    )
    organization_type = models.CharField('Тип организации', max_length=20, choices=ORGANIZATION_TYPES)
    
    # Реквизиты
    inn = models.CharField('ИНН', max_length=12, unique=True)
    kpp = models.CharField('КПП', max_length=9, blank=True)
    ogrn = models.CharField('ОГРН', max_length=15, blank=True)
    legal_address = models.TextField('Юридический адрес')
    
    # Контакты
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    
    # Метаданные
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Project(models.Model):
    """Модель проекта благоустройства"""
    
    PROJECT_STATUSES = [
        ('planning', 'Планирование'),
        ('in_progress', 'В работе'),
        ('suspended', 'Приостановлен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    PROJECT_TYPES = [
        ('landscaping', 'Благоустройство'),
        ('road_construction', 'Дорожное строительство'),
        ('utilities', 'Коммунальные работы'),
        ('renovation', 'Реновация'),
        ('infrastructure', 'Инфраструктура'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название проекта', max_length=500)
    code = models.CharField('Код проекта', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    
    # Тип и статус
    project_type = models.CharField('Тип проекта', max_length=20, choices=PROJECT_TYPES)
    status = models.CharField('Статус', max_length=20, choices=PROJECT_STATUSES, default='planning')
    
    # Организации
    customer = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='customer_projects',
        verbose_name='Заказчик'
    )
    contractor = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='contractor_projects',
        verbose_name='Подрядчик'
    )
    supervisor = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='supervised_projects',
        verbose_name='Надзорный орган',
        null=True,
        blank=True
    )
    
    # Местоположение
    address = models.TextField('Адрес объекта')
    latitude = models.DecimalField('Широта', max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField('Долгота', max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Даты
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    actual_start_date = models.DateField('Фактическая дата начала', null=True, blank=True)
    actual_end_date = models.DateField('Фактическая дата окончания', null=True, blank=True)
    
    # Бюджет
    budget = models.DecimalField('Бюджет', max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField('Фактическая стоимость', max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code}: {self.name}"
    
    @property
    def is_overdue(self):
        """Проверка просрочки проекта"""
        if self.end_date and self.status != 'completed':
            return timezone.now().date() > self.end_date
        return False
    
    @property
    def progress_percentage(self):
        """Расчет процента выполнения"""
        if not self.start_date or not self.end_date:
            return 0
        
        total_days = (self.end_date - self.start_date).days
        if total_days <= 0:
            return 100
        
        elapsed_days = (timezone.now().date() - self.start_date).days
        if elapsed_days <= 0:
            return 0
        elif elapsed_days >= total_days:
            return 100
        
        return round((elapsed_days / total_days) * 100, 1)


class ProjectPhase(models.Model):
    """Модель этапа проекта"""
    
    PHASE_STATUSES = [
        ('not_started', 'Не начат'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('on_hold', 'Приостановлен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name='Проект')
    name = models.CharField('Название этапа', max_length=200)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=1)
    
    # Статус и даты
    status = models.CharField('Статус', max_length=20, choices=PHASE_STATUSES, default='not_started')
    planned_start_date = models.DateField('Плановая дата начала', null=True, blank=True)
    planned_end_date = models.DateField('Плановая дата окончания', null=True, blank=True)
    actual_start_date = models.DateField('Фактическая дата начала', null=True, blank=True)
    actual_end_date = models.DateField('Фактическая дата окончания', null=True, blank=True)
    
    # Бюджет этапа
    budget = models.DecimalField('Бюджет этапа', max_digits=12, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField('Фактическая стоимость', max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        db_table = 'project_phases'
        verbose_name = 'Этап проекта'
        verbose_name_plural = 'Этапы проектов'
        ordering = ['project', 'order']
        unique_together = ['project', 'order']
    
    def __str__(self):
        return f"{self.project.code} - Этап {self.order}: {self.name}"
