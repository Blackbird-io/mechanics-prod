from .base import *

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
# Logging settings
LOGGING_ROOT = '/var/log/django'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
        'error_file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'error.log'),
            'formatter': 'verbose'
        },
        'security_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'security.log'),
            'formatter': 'verbose'
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'debug.log'),
            'formatter': 'verbose'
        },
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'app.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['debug_file', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'blackbird_engine': {
            'handlers': ['app_file'],
            'level': 'DEBUG',
        }
    },
}

##################################################################
# Email settings
EMAIL_BACKEND = 'django_ses_backend.SESBackend'
AWS_SES_RETURN_PATH = ADMINS[0][1]
AWS_SES_AUTO_THROTTLE = float(os.environ.setdefault("SES_THROTTLE", '0.5'))
AWS_SES_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
AWS_SES_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY

