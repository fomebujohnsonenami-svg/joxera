import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-joxera-dev-key-change-me")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "core",
    "users",
    "jobs",
    "payments",
    "reputation",
    "verification",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "core.middleware.GeoIPMiddleware",
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

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB", "joxera"),
        "USER": os.environ.get("POSTGRES_USER", "joxera"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "joxera"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("THROTTLE_ANON", "100/hour"),
        "user": os.environ.get("THROTTLE_USER", "1000/hour"),
    },
}

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

if os.environ.get("GDAL_LIBRARY_PATH"):
    GDAL_LIBRARY_PATH = os.environ["GDAL_LIBRARY_PATH"]
if os.environ.get("GEOS_LIBRARY_PATH"):
    GEOS_LIBRARY_PATH = os.environ["GEOS_LIBRARY_PATH"]

DEFAULT_COUNTRY = os.environ.get("DEFAULT_COUNTRY", "US")
GEOIP_PATH = BASE_DIR / "geoip"
GEOIP_COUNTRY = os.environ.get("GEOIP_COUNTRY", "GeoLite2-Country.mmdb")

IDENTITY_PROVIDER = os.environ.get("IDENTITY_PROVIDER", "persona")
PERSONA_API_KEY = os.environ.get("PERSONA_API_KEY", "")
PERSONA_TEMPLATE_ID = os.environ.get("PERSONA_TEMPLATE_ID", "")
PERSONA_WEBHOOK_SECRET = os.environ.get("PERSONA_WEBHOOK_SECRET", "")
PERSONA_BASE_URL = os.environ.get("PERSONA_BASE_URL", "https://withpersona.com/api/v1")
VERIFF_API_KEY = os.environ.get("VERIFF_API_KEY", "")
VERIFF_API_SECRET = os.environ.get("VERIFF_API_SECRET", "")
VERIFF_WEBHOOK_SECRET = os.environ.get("VERIFF_WEBHOOK_SECRET", "")
VERIFF_BASE_URL = os.environ.get("VERIFF_BASE_URL", "https://stationapi.veriff.com")

SKILL_EMBEDDING_DIMENSIONS = int(os.environ.get("SKILL_EMBEDDING_DIMENSIONS", "768"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
MATCH_GEO_DECAY_KM = float(os.environ.get("MATCH_GEO_DECAY_KM", "50"))

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
DLOCAL_API_KEY = os.environ.get("DLOCAL_API_KEY", "")
DLOCAL_API_SECRET = os.environ.get("DLOCAL_API_SECRET", "")
DLOCAL_WEBHOOK_SECRET = os.environ.get("DLOCAL_WEBHOOK_SECRET", "")
DLOCAL_WEBHOOK_URL = os.environ.get(
    "DLOCAL_WEBHOOK_URL",
    "http://localhost:8000/api/v3/global/payments/webhook/?provider=dlocal",
)

POW_SIGNING_PRIVATE_KEY = os.environ.get("POW_SIGNING_PRIVATE_KEY", "")
POW_SIGNING_PUBLIC_KEY = os.environ.get("POW_SIGNING_PUBLIC_KEY", "")

ALLOW_KYC_SIMULATION = os.environ.get("ALLOW_KYC_SIMULATION", "False").lower() in ("true", "1", "yes")

# Production security hardening
if DJANGO_ENV == "production" or (not DEBUG and DJANGO_ENV != "test"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "yes")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    if not CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
