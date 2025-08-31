"""
Общие утилиты для проекта Электронный журнал производства работ
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
import re
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class SecurityUtils:
    """Утилиты для работы с безопасностью"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Генерация безопасного токена"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_uuid() -> str:
        """Генерация UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Хеширование пароля с солью"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hash_value: str, salt: str) -> bool:
        """Проверка пароля"""
        password_hash, _ = SecurityUtils.hash_password(password, salt)
        return secrets.compare_digest(password_hash, hash_value)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очистка имени файла от опасных символов"""
        # Удаляем путь
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Разрешенные символы
        allowed_chars = re.compile(r'[^a-zA-Zа-яА-Я0-9._-]')
        filename = allowed_chars.sub('_', filename)
        
        # Ограничиваем длину
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename


class ValidationUtils:
    """Утилиты для валидации данных"""
    
    @staticmethod
    def validate_inn(inn: str) -> bool:
        """Валидация ИНН"""
        if not inn or not inn.isdigit():
            return False
        
        if len(inn) not in [10, 12]:
            return False
        
        if len(inn) == 10:
            # ИНН юридического лица
            coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum = sum(int(inn[i]) * coefficients[i] for i in range(9))
            control_digit = control_sum % 11
            if control_digit > 9:
                control_digit = control_digit % 10
            return int(inn[9]) == control_digit
        
        else:
            # ИНН физического лица
            coefficients1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            coefficients2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            
            control_sum1 = sum(int(inn[i]) * coefficients1[i] for i in range(10))
            control_digit1 = control_sum1 % 11
            if control_digit1 > 9:
                control_digit1 = control_digit1 % 10
            
            control_sum2 = sum(int(inn[i]) * coefficients2[i] for i in range(11))
            control_digit2 = control_sum2 % 11
            if control_digit2 > 9:
                control_digit2 = control_digit2 % 10
            
            return int(inn[10]) == control_digit1 and int(inn[11]) == control_digit2
    
    @staticmethod
    def validate_kpp(kpp: str) -> bool:
        """Валидация КПП"""
        if not kpp or len(kpp) != 9:
            return False
        
        # Первые 4 цифры - код налогового органа
        if not kpp[:4].isdigit():
            return False
        
        # 5-6 символы - причина постановки на учет
        if not kpp[4:6].isalnum():
            return False
        
        # Последние 3 цифры - порядковый номер
        if not kpp[6:].isdigit():
            return False
        
        return True
    
    @staticmethod
    def validate_ogrn(ogrn: str) -> bool:
        """Валидация ОГРН"""
        if not ogrn or not ogrn.isdigit():
            return False
        
        if len(ogrn) not in [13, 15]:
            return False
        
        if len(ogrn) == 13:
            # ОГРН юридического лица
            control_sum = int(ogrn[:12]) % 11
            control_digit = control_sum % 10
            return int(ogrn[12]) == control_digit
        else:
            # ОГРНИП
            control_sum = int(ogrn[:14]) % 13
            control_digit = control_sum % 10
            return int(ogrn[14]) == control_digit
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Валидация координат"""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация номера телефона"""
        # Удаляем все символы кроме цифр и +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем формат российского номера
        patterns = [
            r'^\+7\d{10}$',  # +7XXXXXXXXXX
            r'^8\d{10}$',    # 8XXXXXXXXXX
            r'^7\d{10}$',    # 7XXXXXXXXXX
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Валидация email адреса"""
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False


class DateTimeUtils:
    """Утилиты для работы с датой и временем"""
    
    @staticmethod
    def get_moscow_timezone():
        """Получить московский часовой пояс"""
        import pytz
        return pytz.timezone('Europe/Moscow')
    
    @staticmethod
    def now_moscow():
        """Текущее время в московском часовом поясе"""
        return timezone.now().astimezone(DateTimeUtils.get_moscow_timezone())
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Форматирование длительности в человекочитаемый вид"""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} мин"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} ч {minutes} мин"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days} дн {hours} ч"
    
    @staticmethod
    def get_work_days_between(start_date, end_date) -> int:
        """Подсчет рабочих дней между датами (исключая выходные)"""
        current = start_date
        work_days = 0
        
        while current <= end_date:
            if current.weekday() < 5:  # 0-4 это понедельник-пятница
                work_days += 1
            current += timedelta(days=1)
        
        return work_days


class FileUtils:
    """Утилиты для работы с файлами"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'rtf'}
    ALLOWED_ARCHIVE_EXTENSIONS = {'zip', 'rar', '7z', 'tar', 'gz'}
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Получить расширение файла"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    @staticmethod
    def is_image(filename: str) -> bool:
        """Проверка, является ли файл изображением"""
        extension = FileUtils.get_file_extension(filename)
        return extension in FileUtils.ALLOWED_IMAGE_EXTENSIONS
    
    @staticmethod
    def is_document(filename: str) -> bool:
        """Проверка, является ли файл документом"""
        extension = FileUtils.get_file_extension(filename)
        return extension in FileUtils.ALLOWED_DOCUMENT_EXTENSIONS
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 Б"
        
        size_names = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Получить MIME тип файла по расширению"""
        extension = FileUtils.get_file_extension(filename)
        
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
            'txt': 'text/plain',
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'json': 'application/json',
            'xml': 'application/xml',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed',
        }
        
        return mime_types.get(extension, 'application/octet-stream')


class NumericUtils:
    """Утилиты для работы с числами"""
    
    @staticmethod
    def safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
        """Безопасное преобразование в Decimal"""
        if value is None:
            return default
        
        try:
            if isinstance(value, Decimal):
                return value
            elif isinstance(value, (int, float)):
                return Decimal(str(value))
            elif isinstance(value, str):
                return Decimal(value)
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def format_currency(amount: Decimal, currency: str = 'RUB') -> str:
        """Форматирование валютной суммы"""
        if currency == 'RUB':
            return f"{amount:,.2f} ₽".replace(',', ' ')
        else:
            return f"{amount:,.2f} {currency}".replace(',', ' ')
    
    @staticmethod
    def calculate_percentage(part: Decimal, total: Decimal) -> Decimal:
        """Расчет процента"""
        if total == 0:
            return Decimal('0')
        return (part / total) * Decimal('100')


class TextUtils:
    """Утилиты для работы с текстом"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
        """Обрезка текста с добавлением суффикса"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Очистка текста от лишних пробелов и символов"""
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        # Удаляем пробелы в начале и конце
        text = text.strip()
        return text
    
    @staticmethod
    def generate_slug(text: str) -> str:
        """Генерация slug из текста"""
        # Транслитерация кириллицы
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        text = text.lower()
        
        # Заменяем кириллицу
        for cyrillic, latin in translit_dict.items():
            text = text.replace(cyrillic, latin)
        
        # Оставляем только буквы, цифры и дефисы
        text = re.sub(r'[^a-z0-9-]', '-', text)
        
        # Убираем множественные дефисы
        text = re.sub(r'-+', '-', text)
        
        # Убираем дефисы в начале и конце
        text = text.strip('-')
        
        return text


class CacheUtils:
    """Утилиты для работы с кешем"""
    
    @staticmethod
    def generate_cache_key(*args) -> str:
        """Генерация ключа кеша"""
        key_parts = []
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            elif hasattr(arg, 'pk'):
                key_parts.append(f"{arg.__class__.__name__}_{arg.pk}")
            else:
                key_parts.append(str(hash(str(arg))))
        
        return ':'.join(key_parts)
    
    @staticmethod
    def get_cache_timeout(timeout_type: str) -> int:
        """Получить таймаут кеша по типу"""
        timeouts = {
            'short': 5 * 60,      # 5 минут
            'medium': 30 * 60,    # 30 минут
            'long': 60 * 60,      # 1 час
            'daily': 24 * 60 * 60, # 1 день
            'weekly': 7 * 24 * 60 * 60, # 1 неделя
        }
        return timeouts.get(timeout_type, 15 * 60)  # по умолчанию 15 минут


class ErrorUtils:
    """Утилиты для работы с ошибками"""
    
    @staticmethod
    def format_validation_errors(errors: Dict[str, List[str]]) -> str:
        """Форматирование ошибок валидации"""
        formatted_errors = []
        for field, field_errors in errors.items():
            for error in field_errors:
                formatted_errors.append(f"{field}: {error}")
        return '; '.join(formatted_errors)
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Безопасное преобразование в int"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Безопасное преобразование в float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
