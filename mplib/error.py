from django.core import exceptions
from functools import wraps
from rest_framework.response import Response


class SessionException(Exception):
    def __init__(self, err='Session错误'):
        self.error_msg = err
        super().__init__(self, err)

    def __str__(self):
        return self.error_msg


def trouble_shooter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except exceptions.ObjectDoesNotExist as _:
            return Response({'status': 1, 'err_msg': 'LOGIN_FAILED'})
    return wrapper
