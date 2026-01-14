from .base import *
from dotenv import load_dotenv
import os

load_dotenv()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Используем обычное хранилище для статических файлов в разработке
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"


try:
    from .local import *
except ImportError:
    pass
