import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import (
    ProtocolTypeRouter,
    URLRouter,
)

from channels.security.websocket import (
    AllowedHostsOriginValidator,
)

# Adjust middleware path to match your project
from websocket.middleware import JWTAuthMiddleware

# Separate routing imports
from chat.routing import websocket_urlpatterns as chat_routes
from websocket.routing import websocket_urlpatterns as location_routes


application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter([
                *chat_routes,
                *location_routes,
            ])
        )
    ),
})