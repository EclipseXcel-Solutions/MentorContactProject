from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', True)

ALLOWED_HOSTS = ['*']


INSTALLED_APPS += [
    'users',
    'analytics',
    'form'
]


# DATABASES = {
#     'default': {

#         'ENGINE': 'django.db.backends.postgresql_psycopg2',

#         'NAME': os.environ.get('DATABASE_NAME'),

#         'USER': os.environ.get('DATABASE_USER'),

#         'PASSWORD': os.environ.get('DATABASE_PASSWORD'),

#         'HOST': os.environ.get('DATABASE_HOST'),

#         'PORT': os.environ.get('DATABASE_PORT'),

#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        # Optional settings for better performance
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,  # Connection persistence in seconds
        'OPTIONS': {
            'timeout': 20,  # Database timeout in seconds
        },
    }
}


STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]
