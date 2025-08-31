from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class JournalEntry(models.Model):
    """Модель записи в журнале производства работ"""
    
    WORK_TYPES = [
        ('preparation', 'Подготовительные работы'),
        ('excavation', 'Земляные работы'),
        ('foundation', 'Фундаментные работы'),
        ('construction', 'Строительные работы'),
        ('landscaping', 'Благоустройство'),
        ('finishing', 'Отделочные работы'),
        ('utilities', 'Коммунальные работы'),
        ('testing', 'Испытания'),
        ('acceptance', 'Приемочные работы'),
        ('other', 'Прочие работы'),
    ]
    
    WEATHER_CONDITIONS = [
        ('clear', 'Ясно'),
        ('cloudy', 'Облачно'),
        ('overcast', 'Пасмурно'),
        ('rain', 'Дождь'),
        ('snow', 'Снег'),
        ('fog', 'Туман'),
        ('wind', 'Ветер'),
    ]
    
    ENTRY_STATUSES = [
        ('draft', 'Черновик'),
        ('submitted', 'Подана'),
        ('approved', 'Утверждена'),
        ('rejected', 'Отклонена'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='journal_entries',
        verbose_name='Проект'
    )
    
    # Основная информация
    entry_date = models.DateField('Дата записи', default=timezone.now)
    work_type = models.CharField('Тип работ', max_length=20, choices=WORK_TYPES)
    work_description = models.TextField('Описание выполненных работ')
    location = models.CharField('Место выполнения работ', max_length=500, blank=True)
    
    # Погодные условия
    weather_condition = models.CharField('Погодные условия', max_length=20, choices=WEATHER_CONDITIONS, blank=True)
    temperature = models.IntegerField('Температура (°C)', null=True, blank=True)
    
    # Ресурсы
    workers_count = models.PositiveIntegerField('Количество рабочих', default=0)
    equipment_used = models.TextField('Используемая техника', blank=True)
    materials_used = models.TextField('Использованные материалы', blank=True)
    
    # Объемы работ
    planned_volume = models.DecimalField('Плановый объем', max_digits=10, decimal_places=3, null=True, blank=True)
    actual_volume = models.DecimalField('Фактический объем', max_digits=10, decimal_places=3, null=True, blank=True)
    unit_of_measurement = models.CharField('Единица измерения', max_length=50, blank=True)
    
    # Качество
    quality_rating = models.PositiveIntegerField(
        'Оценка качества',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='От 1 до 5'
    )
    quality_notes = models.TextField('Замечания по качеству', blank=True)
    
    # Проблемы и задержки
    has_delays = models.BooleanField('Есть задержки', default=False)
    delay_reason = models.TextField('Причина задержки', blank=True)
    delay_duration = models.PositiveIntegerField('Длительность задержки (часы)', null=True, blank=True)
    
    has_issues = models.BooleanField('Есть проблемы', default=False)
    issues_description = models.TextField('Описание проблем', blank=True)
    
    # Безопасность
    safety_incidents = models.BooleanField('Происшествия по безопасности', default=False)
    safety_description = models.TextField('Описание происшествий', blank=True)
    safety_measures = models.TextField('Принятые меры безопасности', blank=True)
    
    # Статус и утверждение
    status = models.CharField('Статус', max_length=20, choices=ENTRY_STATUSES, default='draft')
    
    # Автор записи
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_journal_entries',
        verbose_name='Автор записи'
    )
    
    # Утверждение
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='approved_journal_entries',
        verbose_name='Утвердил',
        null=True,
        blank=True
    )
    approved_at = models.DateTimeField('Дата утверждения', null=True, blank=True)
    
    # Отклонение
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='rejected_journal_entries',
        verbose_name='Отклонил',
        null=True,
        blank=True
    )
    rejected_at = models.DateTimeField('Дата отклонения', null=True, blank=True)
    rejection_reason = models.TextField('Причина отклонения', blank=True)
    
    # Метаданные
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        db_table = 'journal_entries'
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Записи журнала'
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'entry_date']),
            models.Index(fields=['status']),
            models.Index(fields=['work_type']),
        ]
    
    def __str__(self):
        return f"Запись от {self.entry_date} - {self.project.code}"
    
    def approve(self, approved_by):
        """Утверждение записи"""
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.rejected_by = None
        self.rejected_at = None
        self.rejection_reason = ''
        self.save()
    
    def reject(self, rejected_by, reason):
        """Отклонение записи"""
        self.status = 'rejected'
        self.rejected_by = rejected_by
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        self.approved_by = None
        self.approved_at = None
        self.save()
    
    @property
    def completion_percentage(self):
        """Процент выполнения от планового объема"""
        if self.planned_volume and self.actual_volume:
            return round((self.actual_volume / self.planned_volume) * 100, 1)
        return None


class JournalEntryPhoto(models.Model):
    """Модель фотографий к записи журнала"""
    
    PHOTO_TYPES = [
        ('before', 'До начала работ'),
        ('progress', 'В процессе работ'),
        ('after', 'После завершения работ'),
        ('issue', 'Проблема/Дефект'),
        ('material', 'Материалы'),
        ('equipment', 'Техника'),
        ('safety', 'Безопасность'),
        ('other', 'Прочее'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Запись журнала'
    )
    
    photo_type = models.CharField('Тип фотографии', max_length=20, choices=PHOTO_TYPES, default='progress')
    file_id = models.CharField('ID файла', max_length=100)  # ID из файлового сервиса
    filename = models.CharField('Имя файла', max_length=255)
    description = models.TextField('Описание', blank=True)
    
    # Геолокация фото
    latitude = models.DecimalField('Широта', max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField('Долгота', max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Метаданные
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Загрузил')
    uploaded_at = models.DateTimeField('Загружено', auto_now_add=True)
    
    class Meta:
        db_table = 'journal_entry_photos'
        verbose_name = 'Фотография записи'
        verbose_name_plural = 'Фотографии записей'
        ordering = ['photo_type', 'uploaded_at']
    
    def __str__(self):
        return f"Фото: {self.filename} ({self.get_photo_type_display()})"


class WorkCategory(models.Model):
    """Модель категории работ"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название категории', max_length=200)
    code = models.CharField('Код категории', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Родительская категория',
        null=True,
        blank=True
    )
    
    # Нормативы
    standard_duration = models.PositiveIntegerField('Стандартная продолжительность (часы)', null=True, blank=True)
    standard_workers = models.PositiveIntegerField('Стандартное количество рабочих', null=True, blank=True)
    
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    
    class Meta:
        db_table = 'work_categories'
        verbose_name = 'Категория работ'
        verbose_name_plural = 'Категории работ'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class JournalTemplate(models.Model):
    """Модель шаблона записи журнала"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название шаблона', max_length=200)
    work_category = models.ForeignKey(
        WorkCategory,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name='Категория работ'
    )
    
    # Шаблонные поля
    work_description_template = models.TextField('Шаблон описания работ', blank=True)
    equipment_template = models.TextField('Шаблон списка техники', blank=True)
    materials_template = models.TextField('Шаблон списка материалов', blank=True)
    safety_measures_template = models.TextField('Шаблон мер безопасности', blank=True)
    
    # Настройки
    is_default = models.BooleanField('По умолчанию', default=False)
    is_active = models.BooleanField('Активен', default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'journal_templates'
        verbose_name = 'Шаблон записи'
        verbose_name_plural = 'Шаблоны записей'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.work_category.name})"
