from django.utils.deprecation import MiddlewareMixin
import re
from mplib.models import IPKiller
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.utils import timezone

MAX_VISIT = 200
TIME_INTERVAL = 600


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class InterceptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not re.match('^/mp/api', request.path):
            return None
        http_user_agent = request.META.get('HTTP_USER_AGENT')
        http_user_agent = str(http_user_agent).lower()
        if 'py' in http_user_agent or 'ssl' in http_user_agent:
            return JSONResponse({'status': -1, 'err_msg': 'SERVICE_ERROR'}, status=403)
        if 'micromessenger' not in http_user_agent:
            return JSONResponse({'status': -1, 'err_msg': 'SERVICE_ERROR'}, status=403)
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            user_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            user_ip = request.META['REMOTE_ADDR']
        if user_ip == '202.114.65.12':
            return None
        try:
            record = IPKiller.objects.get(ip=user_ip)
            if not record.stats:
                return JSONResponse({'status': -1, 'err_msg': 'SERVICE_ERROR'}, status=403)
        except IPKiller.DoesNotExist:
            IPKiller.objects.create(ip=user_ip, visit=1, time=timezone.now())
            return None
        passed_seconds = (timezone.now() - record.time).seconds
        if record.visit > MAX_VISIT and passed_seconds < TIME_INTERVAL:
            record.stats = False
            record.save()
            return JSONResponse({'status': -1, 'err_msg': 'SERVICE_ERROR'}, status=403)
        else:
            if passed_seconds < TIME_INTERVAL:
                record.visit = record.visit + 1
                record.save()
            else:
                record.visit = 1
                record.time = timezone.now()
                record.save()
        return None

    def process_response(self, request, response):
        return response
