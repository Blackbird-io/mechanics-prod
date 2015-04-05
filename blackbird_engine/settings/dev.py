from .base import *

##################################################################
# Debug settings
DEBUG = True
TEMPLATE_DEBUG = True

##################################################################
# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../db.sqlite3'),
    }
}

##################################################################
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


##################################################################
# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'query_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'queries.log',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['query_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
        }
    },
}