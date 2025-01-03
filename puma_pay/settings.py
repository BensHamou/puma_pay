from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

AUTHENTICATION_BACKENDS = [
    'account.authentication.ApiBackend',
    'django.contrib.auth.backends.ModelBackend',
    ]

with open(os.path.join(BASE_DIR, 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

DEBUG = True

swappable = 'AUTH_USER_MODEL'

AUTH_USER_MODEL = 'account.User'

ADMIN_URL = 'puma_pay/admin/'

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    'django_cleanup.apps.CleanupConfig',
    'django_crontab',
    "account",
    "commercial",
    "bootstrap5",
    "fontawesomefree",
    "django_filters",
    "widget_tweaks",
    "django_extensions",
]

CRONJOBS = [
    ('0 18 * * 5', 'commercial.cron.send_weekly_recap_email'),
    ('0 18 * * *', 'commercial.cron.send_monthly_recap_email'),
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

ROOT_URLCONF = "puma_pay.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'account', 'templates', 'user'), os.path.join(BASE_DIR, 'account', 'templates', 'fragment'),
                 os.path.join(BASE_DIR, 'account', 'templates', 'zone'), os.path.join(BASE_DIR, 'account', 'templates', 'objective'),
                 os.path.join(BASE_DIR, 'commercial', 'templates', 'payment'), os.path.join(BASE_DIR, 'commercial', 'templates', 'bank'),
                 os.path.join(BASE_DIR, 'commercial', 'templates', 'payment_type'), os.path.join(BASE_DIR, 'commercial', 'templates', 'fragment')],
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

WSGI_APPLICATION = "puma_pay.wsgi.application"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    },
    #'default': {
    #  'ENGINE': 'django.db.backends.postgresql',
    #  'NAME': 'PumaPay',
    #  'USER': 'puma_pay',
    #  'PASSWORD': 'puma_pay',
    #  'HOST': '127.0.0.1',
    #  'PORT': '5432',
    #},
    #'default': {
    #  'ENGINE': 'django.db.backends.postgresql',
    #  'NAME': 'PumaPay',
    #  'USER': 'puma_pay',
    #  'PASSWORD': 'puma_pay',
    #  'HOST': '10.10.10.20',
    #  'PORT': '5444',
    #}
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

LANGUAGE_CODE = "fr"

TIME_ZONE = "Africa/Algiers"

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = 'login_success'
LOGOUT_REDIRECT_URL = '/login'

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = 'login_success'
LOGOUT_REDIRECT_URL = '/login'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pumapaiement@gmail.com'
EMAIL_HOST_PASSWORD = 'ctybajcnepviiqah'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'pumapaiement@gmail.com'

