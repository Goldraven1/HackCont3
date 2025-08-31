"""
Testing settings for Journal System project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Use in-memory database for tests
DATABASES['default'] = {
    'ENGINE': 'django.contrib.gis.db.backends.spatialite',
    'NAME': ':memory:',
}

# Cache settings for testing
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
}

# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Media files for testing
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Logging for testing
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['apps']['level'] = 'CRITICAL'

# Disable security features for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
