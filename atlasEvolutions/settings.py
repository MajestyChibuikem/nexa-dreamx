from pathlib import Path
from utils.env_utils import get_env_variable
import os
from dotenv import load_dotenv
import dj_database_url


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("SECRET_KEY", "fallback-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for Allauth
    "django.contrib.humanize",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "cloudinary",
    "cloudinary_storage",
    # Local apps
    "app.apps.AppConfig",
    "users.apps.UsersConfig",
    "_user.apps.UserConfig",
    "_admin.apps.AdminConfig",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth
]

ACCOUNT_RATE_LIMITS = {
    "change_password": "3/m/user",  # 3 password change requests per user per minute
    "manage_email": "5/m/user",  # 5 email management actions per user per minute
    "reset_password": "10/m/ip,3/m/key",  # 10 password reset requests per minute per IP, 3 per key
    "reauthenticate": "5/m/user",  # 5 reauthentication attempts per user per minute
    "reset_password_from_key": "10/m/ip",  # 10 password resets per IP per minute
    "signup": "10/m/ip",  # 10 signups per IP per minute
    "login": "5/m/ip",  # 5 login attempts per IP per minute
    "login_failed": "5/m/ip,3/5m/key",  # 5 failed login attempts per IP, 3 per 5 minutes per key
    "confirm_email": "1/3m/key",  # 1 email confirmation request every 3 minutes per key
}

ACCOUNT_FORMS = {"signup": "app.forms.CustomSignupForm"}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "atlasEvolutions.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "atlasEvolutions.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("MYSQL_NAME", "mydatabase"),
        "USER": get_env_variable("MYSQL_USER", "myuser"),
        "PASSWORD": get_env_variable("MYSQL_PASSWORD", "mypassword"),
        "HOST": get_env_variable("MYSQL_HOST", "localhost"),
        "PORT": get_env_variable("MYSQL_PORT", "5432"),
    }
}

# DATABASES = {
#     "default": dj_database_url.config(
#         default=get_env_variable(
#             "EXTERNAL_DB_URL", "postgres://user:password@localhost:5432/mydatabase"
#         ),
#         conn_max_age=600,
#         ssl_require=True,
#     )
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER", "your-email@example.com")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD", "your-email-password")

DEFAULT_FROM_EMAIL = get_env_variable("DEFAULT_FROM_EMAIL")
SUPPORT_EMAIL = get_env_variable("SUPPORT_EMAIL")
ADMIN_EMAIL = get_env_variable("ADMIN_EMAIL")

LOGIN_REDIRECT_URL = "/dashboard/"  # Redirect after login
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # Redirect after logout
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_EMAIL_VERIFICATION = "optional"  # Options: 'mandatory', 'optional', 'none'

AUTH_USER_MODEL = "users.CustomUser"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": "dr2z4ackb",
    "API_KEY": "725677599614463",
    "API_SECRET": "b8Cvdw1axYwSNb0egf4hHKQRVMw",
}

ACCOUNT_EMAIL_SUBJECT_PREFIX = ""

APP_URL = get_env_variable("APP_URL")
