"""
Django settings
"""

import os
import wget

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import of model and nomenclature from s3 if specified, if not download from url, or if not local availability is required
if os.getenv("s3_endpoint")!=None:
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': os.getenv("s3_endpoint")},key= os.getenv("s3_access_key"), secret=os.getenv("s3_secret_key")) 
    fs.get(os.getenv("nomenclature"), os.path.join(BASE_DIR+"/nomenclature.csv"))
    fs.get(os.getenv("model"), os.path.join(BASE_DIR+"/model.ftz"))
else:	
    if os.getenv("model")!=None:
    	wget.download(os.getenv("model"), os.path.join(BASE_DIR+"/model.ftz"))
    if (os.getenv("nomenclature")!=None):
        wget.download(os.getenv("nomenclature"), os.path.join(BASE_DIR+"/nomenclature.csv"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = os.path.join(BASE_DIR, 'file')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps
    'apps.endpoints',
    'apps.ml'
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

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
		"django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if os.getenv("db_type")=="postgres":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('db_name'),
            'USER': os.getenv('db_user'),
            'PASSWORD': os.getenv('db_password'),
            'HOST': os.getenv('db_host', 'localhost'),
            'PORT': os.getenv('db_port', '5432'),
        }
    }    
else:
    DATABASES = {
        "default": {
            "ENGINE" : "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3")
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

