import re

from django.conf import settings
from django.http import HttpResponse

ALLOWED_ORIGIN_REGEX = re.compile(
    r"^https?://("
    r"localhost"
    r"|127\.0\.0\.1"
    r"|\[::1\]"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
    r")(:\d+)?$"
)


def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return False
    if origin in settings.CORS_ALLOWED_ORIGINS:
        return True
    return bool(ALLOWED_ORIGIN_REGEX.match(origin))


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin", "")

        if request.method == "OPTIONS" and is_allowed_origin(origin):
            response = HttpResponse(status=200)
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = (
                "Authorization, Content-Type, Accept, Origin, X-Requested-With"
            )
            response["Access-Control-Max-Age"] = "86400"
            return response

        response = self.get_response(request)

        if is_allowed_origin(origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Vary"] = "Origin"

        return response
