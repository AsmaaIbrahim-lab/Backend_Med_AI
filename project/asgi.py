# asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chat.middleware import JWTAuthMiddleware
from chat.routing import websocket_urlpatterns as chat_ws
#from notifications.routing import websocket_urlpatterns as notifications_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                chat_ws #+ notifications_ws
            )
        )
    ),
})
