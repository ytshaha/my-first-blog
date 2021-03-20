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
# BASE_LOCAL_DIR = Path(__file__).resolve().parent.parent

# BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '30gkclf)zp_aa8*_@otx!)3q=z1@&9leo$klr_htq278r^w^++'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '.pythonanywhere.com', '0.0.0.0', 'localhost']

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'taesun.yoo@gmail.com' 
EMAIL_HOST_PASSWORD = 'Stock1holm3#'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'MOUM8 ecommerce <taesun.yoo@gmail.com>'
BASE_URL = 'http://127.0.0.1:8000'
# 쥐메일생일 1986.1.15
# 임시계정 moum8.mailing@gmail.com
# 비번 : moum8admin3#
MANAGERS = (
    ("Taesun Yoo", "taesun.yoo@gmail.com"),
)

ADMIN = MANAGERS



IAMPORT_CODE = 'imp30832141'
IMPORT_REST_API_KEY = '8306112827056798'
IMPORT_REST_API_SECRET = 'WmAHFCAyZFfaMy10g6xRPvFawuuJAVPxiqfY2Pw2uMcgkegAlOsak7kQCOzdKpK2PZ0RPxTjj6AEkQfF'

COOLSMS_REST_API_KEY = 'NCSCDHWYHXRIKCM7'
COOLSMS_REST_API_SECRET = 'TX8TJ7GOHWBKI6BAZNCSXGAJ4CBAVZFO'



GMAIL_API_CREDENTIAL_DIRS = os.path.join(BASE_DIR, 'mysite', 'client.json')
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
]

AUTH_USER_MODEL = 'accounts.User' #changes the built-in user model.
LOGIN_URL = '/login/'
LOGIN_URL_REDIRECT = '/'
LOGOUT_URL = '/logout/'

STRIPE_SECRET_KEY = "sk_test_51IKQwOCVFucPeMu3u9m60jSPGBQhXrHPPfiCoRC1SDPg8CdVLLEVnZExC79i3NaMVU5kgDADgoCffTq7AsKPvwxy00065IC9BM"
STRIPE_PUB_KEY = "pk_test_51IKQwOCVFucPeMu3FS46t1eZG8bfs5elOnEvuL878YygdQmsR485txEKT2bL0qd5LXdV1Qs0eKuMkPdPRcWH6GRR00DNZK6kv0"

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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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

CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "http://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False

AWS_DEFAULT_ACL = None