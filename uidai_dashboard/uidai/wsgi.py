"""WSGI config for UIDAI Dashboard."""
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uidai.settings')
application = get_wsgi_application()
