"""
WSGI config for auth project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
from env import read_dotenv

read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

application = get_wsgi_application()
