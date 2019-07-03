from django.core import exceptions
from functools import wraps
from rest_framework.response import Response
from requests import RequestException


class SessionException(Exception):
    def __init__(self, err='Session错误'):
        self.error_msg = err
        super().__init__(self, err)

    def __str__(self):
        return self.error_msg


class WxAuthException(Exception):
    def __init__(self, err_code=0):
        if err_code == 40029:
            self.error_msg = 'INVALID_CODE'
        elif err_code == -1:
            self.error_msg = 'SYSTEM_BUSY'
        else:
            self.error_msg = 'UNKNOWN_ERROR'
        super().__init__(self, self.error_msg)

    def __str__(self):
        return self.error_msg


def trouble_shooter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.ObjectDoesNotExist as _:
            return Response({'status': 1, 'err_msg': 'LOGIN_FAILED'})
        except WxAuthException as e:
            return Response({'status': 2, 'err_msg': e})
        except RequestException as _:
            return Response({'status': 3, 'err_msg': 'SERVER_NETWORK_ERROR'})
    return wrapper
