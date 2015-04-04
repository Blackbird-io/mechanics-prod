from .base import *

# TODO set this up. See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/
# TODO https://docs.djangoproject.com/en/1.7/ref/settings/

##################################################################
# Debug settings
DEBUG = False
TEMPLATE_DEBUG = False

##################################################################
# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.setdefault("BLACKBIRD_DB_NAME", 'blackbird_engine'),
        'USER': os.environ.setdefault("BLACKBIRD_DB_USER", 'postgres'),
        'PASSWORD': os.environ.setdefault("BLACKBIRD_DB_PASS", 'admin'),
        'HOST': os.environ.setdefault("BLACKBIRD_DB_HOST", 'localhost'),
        'PORT': os.environ.setdefault("BLACKBIRD_DB_PORT", '5432'),
    }
}

##################################################################
# Static file root settings
STATIC_ROOT = os.path.join(BASE_DIR, '../static/')

##################################################################
# Logging settings
LOGGING_ROOT = '/var/log/django'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # TODO this drops sending emails
    'handlers': {
        'error_file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'error.log'),
        },
        'security_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'security.log'),
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'debug.log'),
        },
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'app.log'),
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['debug_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['app_file'],
            'level': 'DEBUG',
        }
    },
}

##################################################################
# Email settings
# TODO
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(LOGGING_ROOT, 'email.log')

