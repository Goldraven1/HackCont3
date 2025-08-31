"""
Модели пользователей и организаций для системы электронного журнала.
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
import uuid


class Organization(models.Model):
    """Модель организации"""
    
    ORGANIZATION_TYPES = [
        ('government', 'Государственный контролирующий орган'),
        ('customer', 'Заказчик'),
        ('contractor', 'Генеральный подрядчик'),
        ('subcontractor', 'Субподрядчик'),
        ('supervisor', 'Технический надзор'),
        ('author_supervision', 'Авторский надзор'),
        ('geodesy', 'Геодезическая организация'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Наименование', max_length=255)
    short_name = models.CharField('Краткое наименование', max_length=100, blank=True)
    organization_type = models.CharField(
        'Тип организации', 
        max_length=50, 
        choices=ORGANIZATION_TYPES
    )
    inn = models.CharField(
        'ИНН', 
        max_length=12, 
        validators=[RegexValidator(r'^\d{10,12}$')],
        unique=True
    )
    kpp = models.CharField(
        'КПП', 
        max_length=9, 
        validators=[RegexValidator(r'^\d{9}$')],
        blank=True
    )
    ogrn = models.CharField(
        'ОГРН', 
        max_length=15, 
        validators=[RegexValidator(r'^\d{13,15}$')],
        blank=True
    )
    address = models.TextField('Юридический адрес', blank=True)
    contact_email = models.EmailField('Контактный email', blank=True)
    contact_phone = models.CharField('Контактный телефон', max_length=20, blank=True)
    
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['name']
    
    def __str__(self):
        return self.short_name or self.name


class User(AbstractUser):
    """Расширенная модель пользователя"""
    
    USER_ROLES = [
        ('admin', 'Администратор системы'),
        ('government_inspector', 'Государственный инспектор'),
        ('customer_manager', 'Представитель заказчика'),
        ('contractor_manager', 'Руководитель подрядчика'),
        ('site_manager', 'Производитель работ'),
        ('technical_supervisor', 'Технический надзор'),
        ('author_supervisor', 'Авторский надзор'),
        ('geodesist', 'Геодезист'),
        ('quality_controller', 'Контролер качества'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    middle_name = models.CharField('Отчество', max_length=50, blank=True)
    phone = models.CharField(
        'Телефон', 
        max_length=20, 
        blank=True,
        validators=[RegexValidator(r'^\+?7\d{10}$')]
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Организация',
        related_name='users'
    )
    role = models.CharField('Роль', max_length=50, choices=USER_ROLES)
    position = models.CharField('Должность', max_length=100, blank=True)
    
    # ЕСИА интеграция
    esia_id = models.CharField('ЕСИА ID', max_length=50, blank=True, unique=True, null=True)
    snils = models.CharField(
        'СНИЛС', 
        max_length=14, 
        blank=True,
        validators=[RegexValidator(r'^\d{3}-\d{3}-\d{3} \d{2}$')]
    )
    inn_personal = models.CharField(
        'ИНН физ. лица', 
        max_length=12, 
        blank=True,
        validators=[RegexValidator(r'^\d{12}$')]
    )
    
    # Дополнительные поля
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    timezone = models.CharField('Часовой пояс', max_length=50, default='Europe/Moscow')
    language = models.CharField('Язык', max_length=10, default='ru')
    
    # Системные поля
    is_verified = models.BooleanField('Подтвержден', default=False)
    last_login_ip = models.GenericIPAddressField('IP последнего входа', blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField('Неудачные попытки входа', default=0)
    locked_until = models.DateTimeField('Заблокирован до', blank=True, null=True)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name.strip() or self.username
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        return self.__str__()
    
    def get_short_name(self):
        """Возвращает краткое имя пользователя"""
        return f"{self.last_name} {self.first_name[:1]}."
    
    @property
    def is_government_inspector(self):
        """Проверяет, является ли пользователь государственным инспектором"""
        return self.role == 'government_inspector'
    
    @property
    def is_contractor(self):
        """Проверяет, является ли пользователь представителем подрядчика"""
        return self.role in ['contractor_manager', 'site_manager']


class UserPermission(models.Model):
    """Дополнительные разрешения пользователей"""
    
    PERMISSION_TYPES = [
        ('project_access', 'Доступ к проекту'),
        ('object_access', 'Доступ к объекту'),
        ('read_only', 'Только чтение'),
        ('full_access', 'Полный доступ'),
        ('reporting', 'Доступ к отчетам'),
        ('admin_panel', 'Доступ к админ-панели'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='permissions'
    )
    permission_type = models.CharField('Тип разрешения', max_length=50, choices=PERMISSION_TYPES)
    object_id = models.UUIDField('ID объекта', blank=True, null=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Предоставлено пользователем',
        related_name='granted_permissions'
    )
    granted_at = models.DateTimeField('Дата предоставления', auto_now_add=True)
    expires_at = models.DateTimeField('Срок действия', blank=True, null=True)
    is_active = models.BooleanField('Активно', default=True)
    
    class Meta:
        verbose_name = 'Разрешение пользователя'
        verbose_name_plural = 'Разрешения пользователей'
        unique_together = ['user', 'permission_type', 'object_id']
    
    def __str__(self):
        return f"{self.user} - {self.get_permission_type_display()}"


class UserSession(models.Model):
    """Сессии пользователей для аудита"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='sessions'
    )
    session_key = models.CharField('Ключ сессии', max_length=40, unique=True)
    ip_address = models.GenericIPAddressField('IP адрес')
    user_agent = models.TextField('User Agent', blank=True)
    location = models.PointField('Геолокация', blank=True, null=True)
    device_info = models.JSONField('Информация об устройстве', blank=True, null=True)
    
    created_at = models.DateTimeField('Начало сессии', auto_now_add=True)
    last_activity = models.DateTimeField('Последняя активность', auto_now=True)
    ended_at = models.DateTimeField('Окончание сессии', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.created_at}"
