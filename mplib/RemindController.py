from apscheduler.schedulers.background import BackgroundScheduler
import requests
from mplib.error import WxAuthException
from mplib.models import Reminder
from datetime import datetime
from django.utils import timezone


class RemindController(object):
    def __init__(self):
        self.access_token = None
        self.update_access_token()
        self.appid = 'wx8ae3e8607ee301fd'
        self.secret = 'df249bf353c20060748c5e40a334ad62'
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update_access_token, 'interval', seconds=7200, id='update access token')
        self.scheduler.add_job(self.check_reminder, 'interval', seconds=3600, id='send remind message')

    def update_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        querystring = {'grant_type': 'client_credential', 'appid': self.appid, 'secret': self.secret}
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
            'Postman-Token': "5d0be631-8dfa-454c-8194-6437bbcad33d"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = response.json()
        if 'access_token' in result:
            self.access_token = result['access_token']
            print('Update Access Token.')
        else:
            raise WxAuthException(err_code=-1)

    def send_message(self, touser, template_id, page, form_id, data, emphasis_keyword):
        url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send"
        querystring = {'access_token': self.access_token,
                       'touser': touser,
                       'template_id': template_id,
                       'page': page,
                       'form_id': form_id,
                       'data': data,
                       # 'emphasis_keyword': emphasis_keyword
                       }
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
            'Postman-Token': "5d0be631-8dfa-454c-8194-6437bbcad33d"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = response.json()
        if result['errcode'] == 0:
            return 0
        else:
            return 1
            # raise WxAuthException(err_code=result['errcode'])

    def check_reminder(self):
        query = Reminder.objects.filter(time__gte=timezone.now())
        num = 0
        success = 0
        for reminder in query:
            r = self.send_message(touser=reminder.openId,
                                  template_id=reminder.templateId,
                                  page=reminder.page,
                                  form_id=reminder.formId,
                                  data=reminder.data,
                                  emphasis_keyword=None)
            if r == 0:
                success += 1
            num += 1
        print('send %d messgae, %d succeed' % (num, success))
