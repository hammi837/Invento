"""
Development settings — never use in production.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts locally
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Add debug toolbar
INSTALLED_APPS += ['debug_toolbar']  # noqa: F405

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa: F405

INTERNAL_IPS = ['127.0.0.1']

# Relax CORS in development — allow Vite dev server
CORS_ALLOW_ALL_ORIGINS = True  # Overrides CORS_ALLOWED_ORIGINS in dev only

# Show emails in console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SQLite fallback for development (no PostgreSQL required)
# Comment this out if you have PostgreSQL running locally
import os  # noqa: E402
if os.environ.get('USE_SQLITE', 'false').lower() == 'true':
    DATABASES = {  # noqa: F405
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }
