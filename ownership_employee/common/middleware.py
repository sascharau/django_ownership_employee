from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.wsgi import WSGIRequest
from .utils import set_current_user


class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest) -> None:
        set_current_user(getattr(request, 'user', None))
