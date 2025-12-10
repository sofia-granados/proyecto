"""
backend_mascotas/settings.py
CONFIGURACIÓN COMPLETA Y CORREGIDA
"""

import os
from pathlib import Path

# ==========================================
# CONFIGURACIÓN BÁSICA
# ==========================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-chofys-pets-2025-secret-key-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ==========================================
# CONFIGURACIÓN DE APLICACIONES
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_mascotas',  # Tu aplicación
]

# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app_mascotas.middleware.RoleRedirectMiddleware',
]

# ==========================================
# CONFIGURACIÓN DE URLS
# ==========================================

ROOT_URLCONF = 'backend_mascotas.urls'

# ==========================================
# CONFIGURACIÓN DE TEMPLATES (¡CORREGIDO!)
# ==========================================

# Ruta para templates (¡CORRECTO con signo = !)
TEMPLATE_DIR = os.path.join(BASE_DIR, 'app_mascotas', 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # ¡AGREGA TODAS ESTAS RUTAS!
            os.path.join(BASE_DIR, 'app_mascotas', 'templates'),
            os.path.join(BASE_DIR, 'templates'),  # Por si acaso
        ],
        'APP_DIRS': True,  # IMPORTANTE: debe ser True
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app_mascotas.context_processors.carrito_context',
            ],
        },
    },
]

# ==========================================
# CONFIGURACIÓN WSGI
# ==========================================

WSGI_APPLICATION = 'backend_mascotas.wsgi.application'

# ==========================================
# BASE DE DATOS
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================================

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

# ==========================================
# INTERNACIONALIZACIÓN
# ==========================================

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ==========================================
# ARCHIVOS ESTÁTICOS
# ==========================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app_mascotas', 'static'),
]

# ==========================================
# ARCHIVOS MEDIA (IMÁGENES)
# ==========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# CONFIGURACIONES PERSONALIZADAS
# ==========================================

# Primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# IVA para México
IVA_PORCENTAJE = 0.16  # 16%

# Configurar modelo de usuario personalizado
AUTH_USER_MODEL = 'app_mascotas.Usuario'

# Configuración de autenticación
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Configuración de login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'