from mplib.XInterface import XInterface
from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework_swagger.views import get_swagger_view
from datetime import datetime
from django.utils import timezone
import json
import requests
import uuid
from mplib import serializers, models
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from mplib.encryption import PRIVATE_KEY
from django.contrib.auth.hashers import make_password, check_password


class TimeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        time = request.query_params.get('time', None)
        if time is not None:
            return queryset.filter(year=time)
        else:
            return queryset


class TypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        type = request.query_params.get('type', None)
        if type is not None:
            return queryset.filter(type=type)
        else:
            return queryset

# Create your views here.


def check_session(session):
    user = models.User.objects.get(session=session)
    if (timezone.now() - user.sessionDate).total_seconds() > 120:
        new_session = uuid.uuid1()
        user.session = new_session
        user.sessionDate = timezone.now()
        user.save()
        return new_session
    else:
        return session


class SessionFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        session = request.query_params.get('session', None)
        if session is not None:
            return queryset.filter(session=session)
        else:
            return queryset


class LibUserViewSet(viewsets.ModelViewSet):
    xi = XInterface(username='miniapp', password='wdlq@2019', alpha_psw='xzw2019')
    queryset = models.LibUser.objects.all()
    serializer_class = serializers.LibUserSerializer

    @action(methods=['get'], detail=False)
    def update_session(self, request):
        self.xi.session = self.xi.login()

    @action(methods=['get'], detail=False)
    def login(self, request):
        key = RSA.importKey(PRIVATE_KEY)
        user = models.User.objects.get(session=request.query_params.get('session', ''))
        rsa_psw = request.query_params.get('libPsw', '')
        clear_psw = PKCS1_v1_5.new(key).decrypt(base64.b64decode(rsa_psw), None).decode()
        auth = self.xi.bor_auth_valid(uid=request.query_params.get('libId', ''),
                                      verification=clear_psw)
        if auth['result'] == 1:
            session = check_session(user.session)
            return Response({'status': 1, 'session': session})
        else:
            try:
                lu = models.LibUser.objects.get(libId=request.query_params.get('libId', ''))
                if not check_password(clear_psw, lu.libPsw):
                    lu.libPsw = make_password(clear_psw)
                    lu.save()
                session = check_session(user.session)
                return Response({'status': 0, 'user': {'name': lu.name, 'bor_id': lu.libId, 'department': lu.department, 'reader_type': lu.readerType}, 'session': session})
            except:
                result_json = {}
                result = self.xi.x_bor_info(bor_id=request.query_params.get('libId', ''))
                for i in result:
                    result_json[i['name']] = i['value']
                lu = models.LibUser(libId=request.query_params.get('libId', ''),
                                    libBorId=result_json['z303_id'],
                                    libPsw=make_password(clear_psw),
                                    name=result_json['reader-name'],
                                    department=result_json['reader-department'],
                                    readerType=result_json['reader-type'],
                                    registrationDate=datetime.strptime(result_json['z305_registration_date'], '%Y%m%d'),
                                    expiryDate=datetime.strptime(result_json['z305_expiry_date'], '%Y%m%d'))
                lu.save()
                session = check_session(user.session)
                return Response({'status': 0, 'user': {'name': lu.name, 'bor_id': lu.libId, 'department': lu.department, 'reader_type': lu.readerType}, 'session': session})

    @action(methods=['get'], detail=False)
    def borrow_info(self, request):
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        return Response({'status': 0, 'result': result['loan'], 'session': session})

    @action(methods=['get'], detail=False)
    def loan_history(self, request):
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.loan_history_detail(bor_id=user.libAccount.libId)
        return Response({'status': 0, 'result': result, 'session': session})

    @action(methods=['get'], detail=False)
    def visit_info(self, request):
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.bor_visit_info(bor_id=user.libAccount.libId)
        return Response({'status': 0, 'result': result, 'session': session})

    @action(methods=['get'], detail=False)
    def hold_info(self, request):
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        return Response({'status': 0, 'result': result['hold'], 'session': session})

    @action(methods=['get'], detail=False)
    def find(self, request):
        session = request.query_params.get('session', '')
        keyword = request.query_params.get('keyword', '')
        lang = request.query_params.get('lang', 'cn')
        code = request.query_params.get('code', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.find(request=keyword, code=code, lang=lang)
        return Response({'status': 0, 'session': session, 'result': result})

    @action(methods=['get'], detail=False)
    def present(self, request):
        session = request.query_params.get('session', '')
        set_num = request.query_params.get('set_num', '')
        entry = request.query_params.get('entry', 1)
        lang = request.query_params.get('lang', 'cn')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        present_info = self.xi.present(set_number=set_num, set_entry=int(entry), lang=lang)
        return Response({'status': 0, 'result': present_info, 'session': session})

    @action(methods=['get'], detail=False)
    def book_detail(self, request):
        session = request.query_params.get('session', '')
        doc_num = request.query_params.get('doc_num', '')
        detail = self.xi.circ_status(sys_no=doc_num)
        user = models.User.objects.get(session=session)
        session = check_session(session)
        return Response({'status': 0, 'result': detail, 'session': session})

    @action(methods=['get'], detail=False)
    def renew(self, request):
        session = request.query_params.get('session', '')
        bar_code = request.query_params.get('bar_code', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.renew(bar_code=bar_code, bor_id=user.libAccount.libId)
        if result['result'] == 0:
            return Response({'status': 0, 'session': session})
        else:
            return Response({'status': 1, 'session': session})

    @action(methods=['get'], detail=False)
    def hold_req(self, request):
        session = request.query_params.get('session', '')
        bar_code = request.query_params.get('bar_code', '')
        pickup_loc = request.query_params.get('pickup', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.hold_req_nlc(bar_code=bar_code, bor_id=user.libAccount.libBorId, pickup_loc=pickup_loc)
        if result['result'] == 0:
            return Response({'status': 0, 'session': session})
        else:
            return Response({'status': 1, 'session': session, 'err_msg': result['err_msg']})

    @action(methods=['get'], detail=False)
    def hold_req_cancel(self, request):
        session = request.query_params.get('session', '')
        doc_number = request.query_params.get('doc_number', '')
        item_sequence = request.query_params.get('item_sequence', '')
        sequence = request.query_params.get('sequence', '')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.hold_req_cancel(doc_number=doc_number, item_sequence=item_sequence, sequence=sequence, bor_id=user.libAccount.libBorId)
        if result['result'] == 0:
            return Response({'status': 0, 'session': session})
        else:
            return Response({'status': 1, 'session': session})

    @action(methods=['get'], detail=False)
    def bor_rank(self, request):
        session = request.query_params.get('session', '')
        lang = request.query_params.get('lang', 'ALL')
        time = request.query_params.get('time', 'y')
        category = request.query_params.get('category', 'ALL')
        user = models.User.objects.get(session=session)
        session = check_session(session)
        result = self.xi.bor_rank(lang=lang, time=time, category=category)
        return Response({'status': 0, 'session': session, 'result': result})

    @action(methods=['get'], detail=False)
    def notice(self, request):
        search = []
        for i in range(20):
            search.append({
                "title": "通知公告",
                "volume": 100,
                "time": "2019-03-26",
                "type": 0
            })
        for i in range(20):
            search.append({
                "title": "通知公告",
                "volume": 100,
                "time": "2019-03-26",
                "type": 1
            })
        for i in range(20):
            search.append({
                "title": "通知公告",
                "volume": 100,
                "time": "2019-03-26",
                "type": 2
            })
        if len(search) > 30:
            search = search[:30]
        return Response(search)

    @action(methods=['get'], detail=False)
    def watch(self, request):
        return Response(self.xi.session)

    @action(methods=['get'], detail=False)
    def fix(self, request):
        self.xi.session = self.xi.login()
        return Response(self.xi.session)


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (SessionFilter,)

    @action(methods=['get'], detail=False)
    def vertify_session(self, request):
        try:
            user = models.User.objects.get(session=request.query_params.get('session', ''))
            if user.libAccount is None:
                session = check_session(user.session)
                return Response({'login': True, 'libBind': False, 'session': session})
            else:
                session = check_session(user.session)
                return Response({'login': True, 'libBind': True, 'session': session})
        except:
            return Response({'login': False, 'libBind': False})

    @action(methods=['get'], detail=False)
    def update_session(self, request):
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        querystring = {'appid': 'wx8ae3e8607ee301fd',
                       'js_code': request.query_params.get('code', ''),
                       'secret': 'df249bf353c20060748c5e40a334ad62',
                       'grant_type': 'authorization_code'}
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "9a482037-e9e8-4b53-9863-3cd0f7864b01"
        }
        response = requests.request("GET", url, data='', headers=headers, params=querystring)
        result = response.json()
        user = models.User.objects.get(session=request.query_params.get('session', ''))
        if result['errorcode'] == 0:
            user.wxSessionKey = result['session_key']
            user.save()
            session = check_session(user.session)
            return Response({'status': 0, 'session': session})
        else:
            session = check_session(user.session)
            return Response({'status': 1, 'session': session})

    @action(methods=['get'], detail=False)
    def login(self, request):
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        querystring = {'appid': 'wx8ae3e8607ee301fd',
                       'js_code': request.query_params.get('code', ''),
                       'secret': 'df249bf353c20060748c5e40a334ad62',
                       'grant_type': 'authorization_code'}
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "9a482037-e9e8-4b53-9863-3cd0f7864b01"
        }
        response = requests.request("GET", url, data='', headers=headers, params=querystring)
        result = response.json()
        openid = result['openid']
        sessionKey = result['session_key']
        nickName = request.query_params.get('nickName', '')
        avatarUrl = request.query_params.get('avatarUrl', '')
        gender = request.query_params.get('gender', '')
        city = request.query_params.get('city', '')
        province = request.query_params.get('province', '')
        country = request.query_params.get('country', '')
        try:
            user = models.User.objects.get(openId=openid)
            if user.libAccount is None:
                return Response({'session': user.session, 'libBind': False})
            else:
                return Response({'session': user.session, 'libBind': True})
        except:
            user = models.User(openId=openid,
                               nickName=nickName,
                               wxSessionKey=sessionKey,
                               avatarUrl=avatarUrl,
                               gender=gender,
                               province=province,
                               city=city,
                               country=country,
                               id=uuid.uuid1(),
                               session=uuid.uuid1(),
                               sessionDate=datetime.now(),
                               lastLoginTime=datetime.now())
            user.save()
            return Response({'session': user.session, 'libBind': False})

    @action(methods=['get'], detail=False)
    def bind_lib(self, request):
        try:
            user = models.User.objects.get(session=request.query_params.get('session', ''))
            libuser = models.LibUser.objects.get(libId=request.query_params.get('libId', ''))
            user.libAccount = libuser
            user.save()
            session = check_session(user.session)
            return Response({'status': 0, 'session': session})
        except:
            return Response({'status': 1})

    @action(methods=['get'], detail=False)
    def unbind_lib(self, request):
        user = models.User.objects.get(session=request.query_params.get('session', ''))
        user.libAccount = None
        user.save()
        session = check_session(user.session)
        return Response({'status': 0, 'session': session})


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Notice.objects.filter(stats=True).order_by('-publishTime')
    serializer_class = serializers.NoticeSerializer
    filter_backends = (TypeFilter, )


schema_view = get_swagger_view(title='Lib Mini Program API', url=None)
