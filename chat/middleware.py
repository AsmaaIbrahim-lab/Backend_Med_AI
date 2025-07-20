# chat/middleware.py
import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token["user_id"]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def _call_(self, scope, receive, send):
        # Extract token from query string: ws://.../?token=abc
        query_string = parse_qs(scope.get("query_string", b"").decode())
        token = query_string.get("token", [None])[0]

        if token is not None:
            try:
                validated_token = UntypedToken(token)
                scope["user"] = await get_user(validated_token)
            except (InvalidToken, TokenError, jwt.exceptions.DecodeError):
                scope["user"] = None
        else:
            scope["user"] = None

        return await super()._call_(scope, receive, send)