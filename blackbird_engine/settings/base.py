"""
Django settings for blackbird_web project.
"""

import os

import requests


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

##################################################################
# Security settings
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.setdefault('DJANGO_SECRET_KEY', '^7+sgz#-hmzhx#h^e#hunx+6s##eiv%^npc&h$g)ca)+0o#11x')
AWS_ACCESS_KEY_ID = os.environ.setdefault('AWS_ACCESS_KEY_ID', 'NEEDKEY')
AWS_SECRET_ACCESS_KEY = os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'NEEDKEY')

hosts = os.environ.setdefault('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = hosts.split(sep=',') if hosts else []
EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

##################################################################
# Email settings (besides backend, which is tier specific)
ADMINS = (('Admin', os.environ.setdefault('ADMIN_EMAIL', 'admin@blackbirdcreditmarket.com')),)
DEFAULT_FROM_EMAIL = os.environ.setdefault('FROM_EMAIL', 'noreply@blackbirdcreditmarket.com')
SERVER_EMAIL = os.environ.setdefault('ERROR_EMAIL', 'errors@blackbirdcreditmarket.com')

##################################################################
# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'rest_framework',
    'json_field',
    'django_ses_backend',
    'dbfiles',
    'blackbird_engine',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

##################################################################
# Uploaded files
MEDIA_URL = '/api/v0/media/'
DEFAULT_FILE_STORAGE = 'dbfiles.storage.DatabaseStorage'

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
# Debug settings
#   Email settings
#   Logging settings