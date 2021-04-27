"""
Django settings for ToyBox project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# from secret_of_settings import SECRET_KEY, DEFAULT_DATABASES_PASSWORD
import ToyBox.secret_of_settings as Secret

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get('SECRET_KEY', 'fifty_random_characters')
SECRET_KEY = Secret.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', '147.230.21.145', '141.101.96.28', '147.230.11.2', '185.155.32.6', '195.113.157.85', '147.230.11.99', '147.230.250.81', )
INTERNAL_IPS = ('127.0.0.1', '147.230.88.184', '127.0.0.1:8000')
# ALLOWED_HOSTS = ['141.101.96.28', '147.230.157.84', 'bedrichov2.tul.cz', '147.230.21.145',]
ALLOWED_HOSTS = ['bedrichov2.tul.cz', '147.230.21.145',]
# if DEBUG:
ALLOWED_HOSTS += ['127.0.0.1', 'localhost', ]


# Application definition

INSTALLED_APPS = [
    'admin_numeric_filter',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mybox.apps.MyboxConfig',

    'daterangefilter',
    'rangefilter',
    'import_export',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    # 'debug_toolbar.panels.redirects.RedirectsPanel',
]

def show_toolbar(request):
    # return request.user.is_staff
    return request.user.is_superuser

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': "ToyBox.settings.show_toolbar",
    #'ENABLE_STACKTRACES_LOCALS': True,
    # 'INTERCEPT_REDIRECTS': False,
}

ROOT_URLCONF = 'ToyBox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # SpeedUp!
            # 'loaders': [
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]


CACHES = {
    # 'default': {
    #     'BACKEND': 'django_redis.cache.RedisCache',
    #     'LOCATION': 'redis://127.0.0.1:6379',
    #     'OPTIONS': {
    #         'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #     },
    #     'KEY_PREFIX': 'myBox'
    # },
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'tmp/',
        # 'LOCATION': 'C:/Users/lukas/Documents/works/Django/ToyBox/tmp',
    }
}

WSGI_APPLICATION = 'ToyBox.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASE_ROUTERS = ['mybox.router.PstDatabaseRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'mybox': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pst',
        'USER': 'postgres',
        'PASSWORD': Secret.DEFAULT_DATABASES_PASSWORD,
        'HOST': 'pg-prod2.nti.tul.cz',
        'PORT': '5432',
        'OPTIONS': {'options': '-c search_path=measurement'},
        'schemas': ['measurement', ],
    },
    # 'mybox': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'pst',
    #     'USER': 'postgres',
    #     # 'PASSWORD': 'Ubuntu',
    #     'HOST': '127.0.0.1',
    #     'PORT': '5433',
    #     'OPTIONS': {'options': '-c search_path=measurement'},
    #     'schemas': ['measurement', ],
    # }
}

IMPORT_EXPORT_USE_TRANSACTIONS = True

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 3, }
    },
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'cs-cz'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Prague'
FIRST_DAY_OF_WEEK = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_ROOT = BASE_DIR / 'static/'
MEDIA_URL = '/files/'