
from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = []


# Application definition



# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}