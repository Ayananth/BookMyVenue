from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User
from accounts.security import decode_access_token


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        user_id = decode_access_token(parts[1])
        if user_id is None:
            raise AuthenticationFailed("Invalid or expired token.")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found.") from exc

        if not user.is_active or user.is_blocked:
            raise AuthenticationFailed("Account is disabled.")

        return (user, parts[1])
