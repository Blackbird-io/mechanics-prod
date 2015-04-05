"""
Django settings for blackbird_web project.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

##################################################################
# Security settings
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.setdefault('DJANGO_SECRET_KEY', '^7+sgz#-hmzhx#h^e#hunx+6s##eiv%^npc&h$g)ca)+0o#11x')

hosts = os.environ.setdefault('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = hosts.split(sep=',') if hosts else []

##################################################################
# Application definition
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'json_field',
    'blackbird_engine',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
)

##################################################################
# Url & wsgi configuration
ROOT_URLCONF = 'blackbird_engine.urls'
WSGI_APPLICATION = 'blackbird_engine.wsgi.application'

##################################################################
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

##################################################################
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static/')


##################################################################
# Environment specific:
# Database settings (https://docs.djangoproject.com/en/1.7/ref/settings/#databases)
#   Debug settings
#   Email settings
#   Logging settings