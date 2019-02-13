from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.wsgi import WSGIRequest
from .utils import set_current_user


# class ThreadLocalMiddleware(object):
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         _thread_locals.request = request
#         return self.get_response(request)
#
#
# class RequestMiddleware(MiddlewareMixin):
#
#     def process_request(self, request):
#         _requests[current_thread().ident] = request
#
#     def process_response(self, request, response):
#         # when response is ready, request should be flushed
#         _requests.pop(current_thread().ident, None)
#         return response
#
#     def process_exception(self, request, exception):
#         # if an exception has happened, request should be flushed too
#         _requests.pop(current_thread().ident, None)
#         raise exception



class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest) -> None:
        set_current_user(getattr(request, 'user', None))
