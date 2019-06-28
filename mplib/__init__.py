from django.apps import AppConfig

default_app_config = 'mplib.MplibConfig'

VERBOSE_APP_NAME = u"小程序后台"


class MplibConfig(AppConfig):
    verbose_name = VERBOSE_APP_NAME
