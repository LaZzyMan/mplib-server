from rest_framework.response import Response
from django.utils.deprecation import MiddlewareMixin


class InterceptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass