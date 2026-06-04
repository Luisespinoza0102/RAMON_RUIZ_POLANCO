import os
from pathlib import Path
# from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-t!=zabhytvk5zc#ps*8wp06!qgw(d%lh7eu!n!&2d5^4mjsn9f'



ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,0.0.0.0').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Mis Apps
    'auditlog',
    'widget_tweaks',
    'tailwind',
    'theme',
    'django_browser_reload',
    'core',
    'catalogo',
    'auditoria',
    'prestamos',
    'recomendacion',
    'reportes',
    'repositorio',
    'estadisticas',
]

TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'prestamos.context_processors.contadores_biblioteca',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ramon_ruiz_polanco',
        'USER': 'Espinoza',
        'PASSWORD': 'luisjose1234',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': (
                "SET sql_mode='STRICT_TRANS_TABLES';"
                "SET innodb_strict_mode=OFF;"
            ),
            'charset': 'utf8'
        }
    },
}



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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'es-ve'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dispatch_dashboard'
LOGOUT_REDIRECT_URL = 'login'

DEBUG = True

# Configuracion de EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Tu dirección de correo completa de Gmail
EMAIL_HOST_USER = 'bibliotecarrpv2.0@gmail.com'

# Los 16 caracteres generados (sin espacios intermedios)
EMAIL_HOST_PASSWORD = 'trnfyaapxuklilja' 

# Dirección por defecto que verán los usuarios al recibir el correo
DEFAULT_FROM_EMAIL = 'Biblioteca Pública Ramón Ruiz Polanco <bibliotecarrpv2.0@gmail.com>'
