import os
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production-please-use-env-variable')
from .base import *

DEBUG = False

# ALLOWED_HOSTS должен быть установлен
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Security settings (опционально, можно закомментировать для разработки)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
