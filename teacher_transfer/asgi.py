"""
ASGI config for teacher_transfer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# teacher_transfer/asgi.py

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import transfers.routing  # Replace 'transfers' with your actual app name if different

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teacher_transfer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            transfers.routing.websocket_urlpatterns
        )
    ),
})
