from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import uuid

User = get_user_model()


class DocumentType(models.Model):
    """Модель типа документа"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название типа', max_length=200)
    code = models.CharField('Код типа', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)
    
    # Настройки
    allowed_extensions = models.CharField(
        'Разрешенные расширения',
        max_length=200,
        default='pdf,doc,docx,xls,xlsx,jpg,jpeg,png',
        help_text='Разделенные запятой расширения файлов'
    )
    max_file_size = models.PositiveIntegerField(
        'Максимальный размер файла (МБ)',
        default=10
    )
    is_required = models.BooleanField('Обязательный', default=False)
    
    # Категоризация
    category = models.CharField('Категория', max_length=100, blank=True)
    
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'document_types'
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документов'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def get_allowed_extensions_list(self):
        """Получить список разрешенных расширений"""
        return [ext.strip() for ext in self.allowed_extensions.split(',')]


class Document(models.Model):
    """Модель документа"""
    
    DOCUMENT_STATUSES = [
        ('draft', 'Черновик'),
        ('review', 'На рассмотрении'),
        ('approved', 'Утвержден'),
        ('rejected', 'Отклонен'),
        ('archived', 'Архивирован'),
    ]
    
    ACCESS_LEVELS = [
        ('public', 'Публичный'),
        ('internal', 'Внутренний'),
        ('confidential', 'Конфиденциальный'),
        ('restricted', 'Ограниченный доступ'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Название документа', max_length=500)
    description = models.TextField('Описание', blank=True)
    
    # Тип и категория
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name='Тип документа'
    )
    
    # Связь с проектом
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Проект',
        null=True,
        blank=True
    )
    
    # Связь с записью журнала
    journal_entry = models.ForeignKey(
        'journal.JournalEntry',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Запись журнала',
        null=True,
        blank=True
    )
    
    # Файл
    file_id = models.CharField('ID файла', max_length=100)  # ID из файлового сервиса
    filename = models.CharField('Имя файла', max_length=255)
    file_size = models.PositiveIntegerField('Размер файла (байты)', default=0)
    file_extension = models.CharField('Расширение файла', max_length=10)
    mime_type = models.CharField('MIME тип', max_length=100, blank=True)
    
    # Версионирование
    version = models.CharField('Версия', max_length=20, default='1.0')
    is_latest_version = models.BooleanField('Последняя версия', default=True)
    parent_document = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Родительский документ',
        null=True,
        blank=True
    )
    
    # Статус и доступ
    status = models.CharField('Статус', max_length=20, choices=DOCUMENT_STATUSES, default='draft')
    access_level = models.CharField('Уровень доступа', max_length=20, choices=ACCESS_LEVELS, default='internal')
    
    # Метаданные
    document_number = models.CharField('Номер документа', max_length=100, blank=True)
    document_date = models.DateField('Дата документа', null=True, blank=True)
    valid_until = models.DateField('Действителен до', null=True, blank=True)
    
    # Подписи и утверждения
    signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='signed_documents',
        verbose_name='Подписал',
        null=True,
        blank=True
    )
    signed_at = models.DateTimeField('Дата подписания', null=True, blank=True)
    digital_signature = models.TextField('Цифровая подпись', blank=True)
    
    # Автор и загрузка
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_documents',
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField('Загружен', auto_now_add=True)
    
    # Обновления
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_documents',
        verbose_name='Обновил',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'documents'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', 'document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['access_level']),
            models.Index(fields=['is_latest_version']),
        ]
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    @property
    def is_expired(self):
        """Проверка истечения срока действия"""
        if self.valid_until:
            return timezone.now().date() > self.valid_until
        return False
    
    def create_new_version(self, file_id, filename, uploaded_by, version=None):
        """Создание новой версии документа"""
        # Убираем флаг последней версии с текущего документа
        self.is_latest_version = False
        self.save()
        
        # Вычисляем новую версию
        if not version:
            try:
                major, minor = map(int, self.version.split('.'))
                version = f"{major}.{minor + 1}"
            except:
                version = "2.0"
        
        # Создаем новую версию
        new_document = Document.objects.create(
            title=self.title,
            description=self.description,
            document_type=self.document_type,
            project=self.project,
            journal_entry=self.journal_entry,
            file_id=file_id,
            filename=filename,
            version=version,
            is_latest_version=True,
            parent_document=self.parent_document or self,
            status='draft',
            access_level=self.access_level,
            document_number=self.document_number,
            document_date=self.document_date,
            valid_until=self.valid_until,
            uploaded_by=uploaded_by
        )
        
        return new_document


class DocumentAccess(models.Model):
    """Модель доступа к документу"""
    
    ACCESS_TYPES = [
        ('read', 'Чтение'),
        ('write', 'Запись'),
        ('delete', 'Удаление'),
        ('admin', 'Администрирование'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_permissions',
        verbose_name='Документ'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_permissions',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    organization = models.ForeignKey(
        'users.Organization',
        on_delete=models.CASCADE,
        related_name='document_permissions',
        verbose_name='Организация',
        null=True,
        blank=True
    )
    
    access_type = models.CharField('Тип доступа', max_length=20, choices=ACCESS_TYPES)
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='granted_document_permissions',
        verbose_name='Предоставил доступ'
    )
    granted_at = models.DateTimeField('Предоставлен', auto_now_add=True)
    
    # Ограничения по времени
    valid_from = models.DateTimeField('Действителен с', null=True, blank=True)
    valid_until = models.DateTimeField('Действителен до', null=True, blank=True)
    
    class Meta:
        db_table = 'document_access'
        verbose_name = 'Доступ к документу'
        verbose_name_plural = 'Доступы к документам'
        unique_together = [
            ['document', 'user', 'access_type'],
            ['document', 'organization', 'access_type'],
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.document.title} - {self.user.get_full_name()} ({self.get_access_type_display()})"
        else:
            return f"{self.document.title} - {self.organization.name} ({self.get_access_type_display()})"
    
    @property
    def is_valid(self):
        """Проверка действительности доступа"""
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True


class DocumentTemplate(models.Model):
    """Модель шаблона документа"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название шаблона', max_length=200)
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name='Тип документа'
    )
    
    # Шаблон
    template_file_id = models.CharField('ID файла шаблона', max_length=100)
    template_filename = models.CharField('Имя файла шаблона', max_length=255)
    
    # Настройки
    is_default = models.BooleanField('По умолчанию', default=False)
    is_active = models.BooleanField('Активен', default=True)
    
    # Поля для заполнения
    required_fields = models.JSONField('Обязательные поля', default=list, blank=True)
    optional_fields = models.JSONField('Опциональные поля', default=list, blank=True)
    
    description = models.TextField('Описание', blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создал')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'document_templates'
        verbose_name = 'Шаблон документа'
        verbose_name_plural = 'Шаблоны документов'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.document_type.name})"


class DocumentWorkflow(models.Model):
    """Модель workflow документа"""
    
    WORKFLOW_STATUSES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='workflows',
        verbose_name='Документ'
    )
    
    workflow_name = models.CharField('Название процесса', max_length=200)
    description = models.TextField('Описание', blank=True)
    
    # Участники
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_workflows',
        verbose_name='Назначен'
    )
    
    # Статус и даты
    status = models.CharField('Статус', max_length=20, choices=WORKFLOW_STATUSES, default='pending')
    started_at = models.DateTimeField('Начат', null=True, blank=True)
    completed_at = models.DateTimeField('Завершен', null=True, blank=True)
    due_date = models.DateTimeField('Срок выполнения', null=True, blank=True)
    
    # Результат
    result = models.TextField('Результат', blank=True)
    comments = models.TextField('Комментарии', blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_workflows',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        db_table = 'document_workflows'
        verbose_name = 'Workflow документа'
        verbose_name_plural = 'Workflows документов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workflow_name} - {self.document.title}"
    
    @property
    def is_overdue(self):
        """Проверка просрочки"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False
