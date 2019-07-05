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
from silk.profiling.profiler import silk_profile
from mplib.error import *
from django.core.exceptions import ObjectDoesNotExist


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


class SessionFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        session = request.query_params.get('session', None)
        if session is not None:
            return queryset.filter(session=session)
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


def check_param(params, request):
    for param in params:
        p = request.query_params.get(param)
        if p is None:
            raise ParamMissException(param)


class LibUserViewSet(viewsets.ReadOnlyModelViewSet):
    xi = XInterface(username='miniapp', password='wdlq@2019', alpha_psw='xzw2019')
    queryset = models.LibUser.objects.all()
    serializer_class = serializers.LibUserSerializer

    def list(self, request, *args, **kwargs):
        return Response('Unsupported Method')

    def retrieve(self, request, *args, **kwargs):
        return Response('Unsupported Method')

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def login(self, request):
        check_param(['session', 'libId', 'libPsw'], request)
        session = request.query_params.get('session')
        key = RSA.importKey(PRIVATE_KEY)
        user = models.User.objects.get(session=session)
        rsa_psw = request.query_params.get('libPsw', '')
        clear_psw = PKCS1_v1_5.new(key).decrypt(base64.b64decode(rsa_psw), None).decode()
        if clear_psw is None:
            raise RSAException()
        self.xi.bor_auth_valid(uid=request.query_params.get('libId'), verification=clear_psw)
        try:
            lu = models.LibUser.objects.get(libId=request.query_params.get('libId', ''))
            if not check_password(clear_psw, lu.libPsw):
                lu.libPsw = make_password(clear_psw)
                lu.save()
            session = check_session(user.session)
            return Response({'status': 0, 'user': {'name': lu.name, 'bor_id': lu.libId, 'department': lu.department,
                                                   'reader_type': lu.readerType}, 'session': session})
        except ObjectDoesNotExist as _:
            result = self.xi.x_bor_info(bor_id=request.query_params.get('libId', ''))
            lu = models.LibUser(libId=request.query_params.get('libId', ''),
                                libBorId=result['z303_id'],
                                libPsw=make_password(clear_psw),
                                name=result['reader-name'],
                                department=result['reader-department'],
                                readerType=result['reader-type'],
                                registrationDate=datetime.strptime(result['z305_registration_date'], '%Y%m%d'),
                                expiryDate=datetime.strptime(result['z305_expiry_date'], '%Y%m%d'))
            lu.save()
            session = check_session(user.session)
            return Response({'status': 0, 'user': {'name': lu.name, 'bor_id': lu.libId, 'department': lu.department,
                                                   'reader_type': lu.readerType}, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def bor_info(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result['bor-info'], 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def borrow_info(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result['loan'], 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def loan_history(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        result = self.xi.loan_history_detail(bor_id=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def fine_info(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result['fine'], 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def visit_info(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_visit_info(bor_id=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def hold_info(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session', '')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_info(uid=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'result': result['hold'], 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def find(self, request):
        check_param(['session', 'keyword'], request)
        session = request.query_params.get('session')
        keyword = request.query_params.get('keyword')
        lang = request.query_params.get('lang', 'cn')
        code = request.query_params.get('code', '')
        result = self.xi.find(request=keyword, code=code, lang=lang)
        user = models.User.objects.get(session=session)
        session = check_session(session)
        return Response({'status': 0, 'session': session, 'result': result})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def present(self, request):
        check_param(['session', 'set_num'], request)
        session = request.query_params.get('session')
        set_num = request.query_params.get('set_num')
        entry = request.query_params.get('entry', 1)
        lang = request.query_params.get('lang', 'cn')
        present_info = self.xi.present(set_number=set_num, set_entry=int(entry), lang=lang)
        user = models.User.objects.get(session=session)
        session = check_session(session)
        return Response({'status': 0, 'result': present_info, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def book_detail(self, request):
        check_param(['session', 'doc_num'], request)
        session = request.query_params.get('session')
        doc_num = request.query_params.get('doc_num')
        detail = self.xi.circ_status(sys_no=doc_num)
        user = models.User.objects.get(session=session)
        session = check_session(session)
        return Response({'status': 0, 'result': detail, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def renew(self, request):
        check_param(['session', 'bar_code'], request)
        session = request.query_params.get('session')
        bar_code = request.query_params.get('bar_code')
        user = models.User.objects.get(session=session)
        self.xi.renew(bar_code=bar_code, bor_id=user.libAccount.libId)
        session = check_session(session)
        return Response({'status': 0, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def hold_req(self, request):
        check_param(['session', 'bar_code', 'pickup'], request)
        session = request.query_params.get('session')
        bar_code = request.query_params.get('bar_code')
        pickup_loc = request.query_params.get('pickup')
        user = models.User.objects.get(session=session)
        self.xi.hold_req_nlc(bar_code=bar_code, bor_id=user.libAccount.libBorId, pickup_loc=pickup_loc)
        session = check_session(session)
        return Response({'status': 0, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def hold_req_cancel(self, request):
        check_param(['session', 'doc_number', 'item_sequence', 'sequence'], request)
        session = request.query_params.get('session')
        doc_number = request.query_params.get('doc_number')
        item_sequence = request.query_params.get('item_sequence')
        sequence = request.query_params.get('sequence')
        user = models.User.objects.get(session=session)
        self.xi.hold_req_cancel(doc_number=doc_number, item_sequence=item_sequence, sequence=sequence, bor_id=user.libAccount.libBorId)
        session = check_session(session)
        return Response({'status': 0, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def bor_rank(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        lang = request.query_params.get('lang', 'ALL')
        time = request.query_params.get('time', 'y')
        category = request.query_params.get('category', 'ALL')
        user = models.User.objects.get(session=session)
        result = self.xi.bor_rank(lang=lang, time=time, category=category)
        session = check_session(session)
        return Response({'status': 0, 'session': session, 'result': result})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def update_email(self, request):
        check_param(['session', 'email'], request)
        session = request.query_params.get('session')
        email = request.query_params.get('email')
        user = models.User.objects.get(session=session)
        self.xi.update_email(bor_id=user.libAccount.libId, email=email)
        session = check_session(session)
        return Response({'status': 0, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def update_telephone(self, request):
        check_param(['session', 'tel'], request)
        session = request.query_params.get('session', '')
        tel = request.query_params.get('tel', '')
        user = models.User.objects.get(session=session)
        self.xi.update_telephone(bor_id=user.libAccount.libId, tel=tel)
        session = check_session(session)
        return Response({'status': 0, 'session': session})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (SessionFilter,)

    def list(self, request, *args, **kwargs):
        return Response('Unsupported Method')

    def retrieve(self, request, *args, **kwargs):
        return Response('Unsupported Method')

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def vertify_session(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        user = models.User.objects.get(session=session)
        if user.libAccount is None:
            session = check_session(user.session)
            return Response({'status': 0, 'login': True, 'libBind': False, 'session': session})
        else:
            session = check_session(user.session)
            return Response({'status': 0, 'login': True, 'libBind': True, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def update_session(self, request):
        check_param(['session', 'code'], request)
        session = request.query_params.get('session')
        code = request.query_params.get('code')
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        querystring = {'appid': 'wx8ae3e8607ee301fd',
                       'js_code': code,
                       'secret': 'df249bf353c20060748c5e40a334ad62',
                       'grant_type': 'authorization_code'}
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "9a482037-e9e8-4b53-9863-3cd0f7864b01"
        }
        response = requests.request("GET", url, data='', headers=headers, params=querystring)
        result = response.json()
        user = models.User.objects.get(session=session)
        if 'errcode' not in result:
            user.wxSessionKey = result['session_key']
            user.save()
            session = check_session(user.session)
            return Response({'status': 0, 'session': session})
        else:
            raise WxAuthException(err_code=result['errcode'])

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def login(self, request):
        check_param(['code'], request)
        code = request.query_params.get('code')
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        querystring = {'appid': 'wx8ae3e8607ee301fd',
                       'js_code': code,
                       'secret': 'df249bf353c20060748c5e40a334ad62',
                       'grant_type': 'authorization_code'}
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "9a482037-e9e8-4b53-9863-3cd0f7864b01"
        }
        response = requests.request("GET", url, data='', headers=headers, params=querystring)
        result = response.json()
        if 'errcode' in result:
            raise WxAuthException(err_code=result['errcode'])
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
                return Response({'status': 0, 'session': user.session, 'libBind': False})
            else:
                return Response({'status': 0, 'session': user.session, 'libBind': True})
        except ObjectDoesNotExist as _:
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
            return Response({'status': 0, 'session': user.session, 'libBind': False})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def bind_lib(self, request):
        check_param(['session', 'libId'], request)
        session = request.query_params.get('session')
        libId = request.query_params.get('libId')
        user = models.User.objects.get(session=session)
        libuser = models.LibUser.objects.get(libId=libId)
        user.libAccount = libuser
        user.save()
        session = check_session(user.session)
        return Response({'status': 0, 'session': session})

    @action(methods=['get'], detail=False)
    @trouble_shooter
    def unbind_lib(self, request):
        check_param(['session'], request)
        session = request.query_params.get('session')
        user = models.User.objects.get(session=session)
        user.libAccount = None
        user.save()
        session = check_session(user.session)
        return Response({'status': 0, 'session': session})


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Notice.objects.filter(stats=True).order_by('-publishTime')
    serializer_class = serializers.NoticeSerializer
    filter_backends = (TypeFilter, )


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    available = models.Activity.objects.filter(stats=True).order_by('-publishTime')
    if len(available) >= 4:
        queryset = available[:4]
    else:
        queryset = models.Activity.objects.filter(stats=True).order_by('-publishTime')
    serializer_class = serializers.ActivitySerializer


class AdviseViewSet(viewsets.ModelViewSet):
    queryset = models.Advise.objects.order_by('-publishTime')
    serializer_class = serializers.AdviseSerializer


schema_view = get_swagger_view(title='Lib Mini Program API', url=None)
