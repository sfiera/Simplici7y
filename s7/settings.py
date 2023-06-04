"""
Django settings for s7 project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

if not os.environ.get("PRODUCTION"):
    load_dotenv()

DEBUG = os.environ.get("DEBUG")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# if not DEBUG:
#     SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
# else:
SECRET_KEY = json.load(open("test_config.json"))["SECRET_KEY"]

ALLOWED_HOSTS = ["simplici7y.herokuapp.com", "simplici7y.com", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "items.apps.ItemsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "imagekit",
    "rest_framework",
    "storages",
    "markdownify",
]

MIDDLEWARE = (
    [
        "django.middleware.security.SecurityMiddleware",
    ]
    + (["whitenoise.middleware.WhiteNoiseMiddleware"] if not DEBUG else [])
    + [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
)

ROOT_URLCONF = "s7.urls"

AUTH_USER_MODEL = "items.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "s7.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES["default"].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "simplici7y"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_LOCATION = "static"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, "media")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Markdownify

MARKDOWNIFY = {
    "default": {
        "STRIP": False,
        "WHITELIST_TAGS": [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "br",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "strong",
            "ul",
        ],
    },
}
