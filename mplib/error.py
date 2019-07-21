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
        elif err_code == 40037:
            self.error_msg = 'TEMPLATE_ID_ERROR'
        elif err_code == 41028:
            self.error_msg = 'FORM_ID_ERROR'
        elif err_code == 41029:
            self.error_msg = 'FORM_ID_USED'
        elif err_code == 41030:
            self.error_msg = 'PAGE_ERROR'
        elif err_code == 45009:
            self.error_msg = 'OVERRUN_LIMIT'
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
            print('ObjectDoesNotExist. Detail: LOGIN_FAILED')
            return Response({'status': 1, 'err_msg': 'LOGIN_FAILED'})
        except WxAuthException as e:
            print('WxAuthException. Detail: %s' % e.error_msg)
            return Response({'status': 2, 'err_msg': e.error_msg})
        except RequestException as _:
            print('RequestException. Detail: SERVER_NETWORK_ERROR')
            return Response({'status': 3, 'err_msg': 'SERVER_NETWORK_ERROR'})
        except ParamMissException as e:
            print('ParamMissException. Detail: %s' % e.error_msg)
            return Response({'status': 4, 'err_msg': e.error_msg})
        except RSAException as _:
            print('RSAException. Detail: RSA_KEY_ERROR')
            return Response({'status': 5, 'err_msg': 'RSA_KEY_ERROR'})
        except LibException as e:
            print('LibException. Detail: %s' % e.error_detail)
            return Response({'status': 6, 'err_msg': e.error_msg, 'detail': e.error_detail})
    return wrapper
