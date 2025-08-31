"""
Development settings for Journal System project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
DATABASES['default'].update({
    'NAME': config('DB_NAME', default='journal_dev'),
    'USER': config('DB_USER', default='journal_user'),
    'PASSWORD': config('DB_PASSWORD', default='journal_pass'),
    'HOST': config('DB_HOST', default='localhost'),
    'PORT': config('DB_PORT', default='5432'),
})

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Additional apps for development
INSTALLED_APPS += [
    'django_extensions',
]

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    # Debug Toolbar Settings
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache settings for development
CACHES['default']['LOCATION'] = config('REDIS_URL', default='redis://localhost:6379/0')

# Static files for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files for development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Logging for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Disable HTTPS redirects in development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Development-specific settings
SHELL_PLUS_PRINT_SQL = True
