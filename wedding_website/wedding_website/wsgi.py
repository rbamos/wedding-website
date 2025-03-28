"""
WSGI config for wedding_website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import json
from django.core.wsgi import get_wsgi_application
import logging

logger = logging.getLogger(__name__)

# Load JSON secrets from /etc/secrets.json
SECRETS_FILE = '/etc/secrets.json'

try:
    with open(SECRETS_FILE, 'r') as secrets_file:
        secrets = json.load(secrets_file)
        # Set secrets as environment variables
        for key, value in secrets.items():
            os.environ[key] = value.__str__()
except FileNotFoundError:
    logger.error(f"Secrets file {SECRETS_FILE} not found.")
except json.JSONDecodeError:
    logger.error(f"Failed to parse JSON from {SECRETS_FILE}.")

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wedding_website.settings')

# Get the WSGI application
application = get_wsgi_application()