import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # Load .env file into environment variables


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h*e%+@evipqxr*-568yx$22cjkz^h(&p7*-ap%wjjs9k(bu4u#'
# SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# Get ENVIRONMENT value from .env
ENVIRONMENT = os.getenv('ENVIRONMENT', 'prod')
# DEBUG = os.getenv('DEBUG', True)
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'



CSRF_TRUSTED_ORIGINS = ["https://api.zefe.xyz", "https://zef.dubinu.com","https://zefe-frontend-khaki.vercel.app/"]


# for development
# CSRF_TRUSTED_ORIGINS = [
#     "https://api.zefe.xyz", 
#     "https://zef.dubinu.com", 
#     "https://5fa8-2400-1a00-bb20-a928-bc40-e9dc-6349-a663.ngrok-free.app",
#     "https://3e3b-2400-1a00-bb20-a928-bc40-e9dc-6349-a663.ngrok-free.app",
#     "http://localhost:3000",
# ]

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'drf_yasg',

    # Local apps
    "user",
    "events",
    "catalog"
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'events.middleware.transaction_middleware.SolanaTransactionMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = []


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# if os.getenv('ENVIRONMENT') == "dev":
#     print("DEVELOPMENT ENVIRONMENT")
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }
# else:

print("HOST", os.getenv("DB_HOST"))

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE') or "django.db.backends.postgresql",
        'NAME': os.getenv('POSTGRES_DB') or os.getenv('DB_NAME')  or "zefe_db",
        'USER': os.getenv('POSTGRES_USER') or os.getenv("DB_USER") or "postgres",
        'PASSWORD': os.getenv('POSTGRES_PASSWORD') or os.getenv("DB_PASSWORD") or "postgres",
        'HOST': os.getenv("DB_HOST") or "localhost",
        'PORT': os.getenv('DB_PORT') or "5432",
    }
}

# DATABASES = {
    # 'default': {
        # 'ENGINE': "django.db.backends.postgresql" or os.getenv('DB_ENGINE') or "django.db.backends.postgresql",
        # 'NAME': "zef" or os.getenv('POSTGRES_DB') or os.getenv('DB_NAME')  or "zefe_db",
        # 'USER': "myuser" or os.getenv('POSTGRES_USER') or os.getenv("DB_USER") or "postgres",
        # 'PASSWORD': "mypassword" or os.getenv('POSTGRES_PASSWORD') or os.getenv("DB_PASSWORD") or "postgres",
        # 'HOST': "localhost" or os.getenv("DB_HOST") or "localhost",
        # 'PORT': "5432" or os.getenv('DB_PORT') or "5432",
        # 
    # }
# }

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
print("STATIC_ROOT",STATIC_ROOT)
# Media files (uploaded files)
MEDIA_URL = '/media/'  # URL prefix for media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Local file system path to store media


DEFAULT_RENDERER_CLASSES = ("core.renderers.CustomJSONRenderer",)


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS':('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'core.renderers.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=3000),  # Token expires in 30 mins
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Refresh token valid for 7 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key',  # Use `env` variables in production
    'AUTH_HEADER_TYPES': ('Bearer',),
}
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTH_USER_MODEL = 'user.User'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# TELEGRAM_BOT_TOKEN = "7768362707:AAEnVm1DYxeKoFgkaVOxfcFyng_vVTNY2og"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")



LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "debug.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "propagate": True,
            "level": "INFO",
        },
        "MYAPP": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}


# for local testing

# from corsheaders.defaults import default_headers

# CORS_ALLOW_HEADERS = list(default_headers) + [
#     'ngrok-skip-browser-warning',
# ]