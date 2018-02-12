import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_network.settings")
os.environ.setdefault('DJANGO_CONFIGURATION', 'DevelopmentConfig')

from configurations.wsgi import get_wsgi_application
application = get_wsgi_application()
