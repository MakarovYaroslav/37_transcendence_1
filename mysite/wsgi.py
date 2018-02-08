"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'DevelopmentConfig')

from configurations.wsgi import get_wsgi_application
application = get_wsgi_application()
