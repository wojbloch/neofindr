from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()
env = os.environ.get

DOCKERIZED = env("DOCKERIZED", False)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY", "")

DEBUG = env("DEBUG", False)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_celery_beat",
    "core",
    "scrapers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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


WSGI_APPLICATION = "config.wsgi.application"


if DOCKERIZED:
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", "django.db.backends.postgresql"),
            "NAME": env("DB_NAME", "neofindr"),
            "USER": env("DB_USER", "postgres"),
            "PASSWORD": env("DB_PASSWORD", "postgres"),
            "HOST": "db",
            "PORT": "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", "django.db.backends.postgresql"),
            "NAME": env("DB_NAME", "neofindr"),
            "USER": env("DB_USER", "postgres"),
            "PASSWORD": env("DB_PASSWORD", "postgres"),
            "HOST": "localhost",
            "PORT": "5432",
        }
    }


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
STATIC_URL = "static/"
STATIC_ROOT = env("STATIC_ROOT", default=f"{BASE_DIR}/static")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
