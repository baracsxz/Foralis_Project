import dj_database_url
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+ew%%h&$f#d+f)p27d%ij=+6a95k0n85k*lts$5zv7g17ln*c+'

DEBUG = True

ALLOWED_HOSTS = ['.render.com', 'localhost', '127.0.0.1', 'foralis-admin.onrender.com']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ADD THIS LINE HERE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foralis_core.urls'

def dashboard_counters(request):
    try:
        from inventory.models import Material, Movement
        total_materials = Material.objects.count()
        total_ingoing = Movement.objects.filter(movement_type__iexact='IN').count()
        total_outgoing = Movement.objects.filter(movement_type__iexact='OUT').count()
        low_stock_materials = Material.objects.filter(current_stock__lte=10)
        low_stock_alerts = low_stock_materials.count()
    except Exception:
        total_materials = total_ingoing = total_outgoing = low_stock_alerts = 0
        low_stock_materials = []

    return {
        'total_materials': total_materials,
        'total_ingoing': total_ingoing,
        'total_outgoing': total_outgoing,
        'low_stock_alerts': low_stock_alerts,
        'low_stock_items': low_stock_materials,
    }

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
                'foralis_core.settings.dashboard_counters',
            ],
        },
    },
]

WSGI_APPLICATION = 'foralis_core.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

if not DATABASES['default']:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Foralis_Database',
        'USER': 'admin',
        'PASSWORD': 'admin2026',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True
USE_L10N = False

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

JAZZMIN_SETTINGS = {
    "site_title": "Foralis Admin Portal",
    "site_header": "Foralis",
    "site_brand": "Foralis Ventures Group",
    "site_logo": "logo.webp",
    "login_logo": "logo.webp",
    "login_logo_styles": "max-height: 160px; width: auto; object-fit: contain; margin: 0 auto; display: block;",
    "site_logo_classes": "img-circle elevation-3",
    "welcome_sign": "Sign in to your inventory management system",
    "copyright": "Foralis Ventures Group",
    "search_model": ["inventory.Material"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth.user": "fas fa-user",
        "inventory.Supplier": "fas fa-truck",
        "inventory.Material": "fas fa-boxes",
        "inventory.Movement": "fas fa-exchange-alt",
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "dark_mode": False,
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "navbar_bg": "navbar-dark",
    "sidebar_bg": "sidebar-dark-primary",
    "accent": "accent-primary",
}

LOGOUT_REDIRECT_URL = '/admin/login/'