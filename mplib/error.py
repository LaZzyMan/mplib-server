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


class ParamMissException(Exception):
    def __init__(self, err='param'):
        self.error_msg = 'PARAM_%s_MISS' % err.upper()
        super().__init__(self, self.error_msg)

    def __str__(self):
        return self.error_msg


class RSAException(Exception):
    pass


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


class LibException(Exception):
    def __init__(self, err_msg='lib error', err_detail=''):
        self.error_msg = err_msg.replace(' ', '_').upper()
        self.error_detail = err_detail
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
            return Response({'status': 2, 'err_msg': e.error_msg})
        except RequestException as _:
            return Response({'status': 3, 'err_msg': 'SERVER_NETWORK_ERROR'})
        except ParamMissException as e:
            return Response({'status': 4, 'err_msg': e.error_msg})
        except RSAException as _:
            return Response({'status': 5, 'err_msg': 'RSA_KEY_ERROR'})
        except LibException as e:
            return Response({'status': 6, 'err_msg': e.error_msg, 'detail': e.error_detail})
    return wrapper
