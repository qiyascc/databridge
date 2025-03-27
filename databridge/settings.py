"""
Django settings for databridge project.

Generated by 'django-admin startproject' using Django 4.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "lcwaikiki",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "databridge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "databridge.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
    # 'default': {
    #     'ENGINE': 'djongo',
    #     'NAME': 'test',
    #     'CLIENT': {
    #         'host': 'mongodb+srv://Q:q@test.2xj08.mongodb.net/test?retryWrites=true&w=majority',
    #         'username': 'Q',
    #         'password': 'q',
    #         'authSource': 'admin',
    #         'authMechanism': 'SCRAM-SHA-1'
    #     },
    # }
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Scrapy settings
SCRAPY_SETTINGS = {
    'BOT_NAME': "databridge_scrapy",
    'SPIDER_MODULES': ["databridge_scrapy.databridge_scrapy.spiders"],
    'NEWSPIDER_MODULE': "databridge.databridge_scrapy.spiders",
    'ROBOTSTXT_OBEY': False,
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_TIMEOUT': 30,
    'DOWNLOAD_DELAY': 1,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'ITEM_PIPELINES': {
        'lcwaikiki.pipelines.DjangoPipeline': 300,
        'databridge_scrapy.databridge_scrapy.pipelines.MongoDBPipeline': 300,
    },
    'RETRY_TIMES': 3,
    'RETRY_HTTP_CODES': [403, 500, 502, 503, 504, 522, 524, 408],
    'DOWNLOADER_MIDDLEWARES': {
        'databridge_scrapy.databridge_scrapy.middlewares.CustomUserAgentMiddleware': 543,
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'databridge_scrapy.databridge_scrapy.middlewares.ProxyMiddleware': 542,
        'databridge_scrapy.databridge_scrapy.middlewares.CustomRetryMiddleware': 541,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    },
    'PROXIES': [
        # Your proxy list here
    ]
}

