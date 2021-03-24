"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.0.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.herokuapp.com', 'moum8.herokuapp.com', 'www.moum8.com']

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'moum8.ecommerce@gmail.com' 
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'MOUM8 ecommerce <moum8.ecommerce@gmail.com>'
BASE_URL = 'https://moum8.herokuapp.com'

MANAGERS = (
    ("MOUM8 ecommerce", "moum8.ecommerce@gmail.com"),
)

ADMIN = MANAGERS


IAMPORT_CODE = os.environ.get('IAMPORT_CODE')
IMPORT_REST_API_KEY = os.environ.get('IMPORT_REST_API_KEY')
IMPORT_REST_API_SECRET = os.environ.get('IMPORT_REST_API_SECRET')

GMAIL_API_CREDENTIAL_DIRS = os.path.join(BASE_DIR, 'mysite', 'client_deploy.json')
# GMAIL_API_CREDENTIAL_DIRS = os.path.join(BASE_DIR, 'mysite', 'client.json')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # third party
    'storages',
    # my app
    'blog',
    'shop',
    'accounts',
    'products',
    'search',
    'tags',
    'carts',
    'orders',
    'billing',
    'addresses',
    'biddings',
    'tickets',
    'points',
    'reviews',
    'staff',
    'wishlist',
]

AUTH_USER_MODEL = 'accounts.User' #changes the built-in user model.
LOGIN_URL = '/login/'
LOGIN_URL_REDIRECT = '/'
LOGOUT_URL = '/logout/'

STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUB_KEY = os.environ.get('STRIPE_PUB_KEY')

COOLSMS_REST_API_KEY = os.environ.get('COOLSMS_REST_API_KEY')
COOLSMS_REST_API_SECRET = os.environ.get('COOLSMS_REST_API_SECRET')



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# add this
import dj_database_url
db_from_env = dj_database_url.config() # postreSQL Database in heroku
DATABASES['default'].update(db_from_env)
DATABASES['default']['CONN_MAX_AGE'] = 500

DATABASE_URL = 'postgresql://mfnwodhpznhpag:974834453a1cda89c465403699a3861f016776e57897619d00ba6fe2103c98ab@ec2-100-24-139-146.compute-1.amazonaws.com:5432/d1n8i6vn5p0psu'
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_my_proj")
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static_cdn','static_root')

LOGIN_REDIRECT_URL = '/product/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static_cdn', 'media_root')


from mysite.aws.conf import *

# https://kirr.co/vklau5

# Let's Encryp ssl/tls https

CORS_REPLACE_HTTPS_REFERER      = True
HOST_SCHEME                     = "https://"
SECURE_PROXY_SSL_HEADER         = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT             = True
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_SECONDS             = 1000000
SECURE_FRAME_DENY               = True