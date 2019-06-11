from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework_swagger.views import get_swagger_view
from datetime import datetime
import json
import requests
import uuid
from mplib import serializers, models

# Create your views here.


class SessionFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        session = request.query_params.get('session', None)
        if session is not None:
            return queryset.filter(session=session)
        else:
            return queryset


class LibUserViewSet(viewsets.ModelViewSet):
    queryset = models.LibUser.objects.all()
    serializer_class = serializers.LibUserSerializer

    @action(methods=['get'], detail=False)
    def login(self, request):
        url = 'http://api.lib.whu.edu.cn/aleph-x/bor/oper'
        payload = 'BorForm%5Busername%5D=miniapp&BorForm%5Bpassword%5D=xzw2019%40wx&BorForm%5Bop%5D=bor-info&BorForm%5Bbor_id%5D=' + request.query_params.get('libId', '') + '&BorForm%5Bop_param%5D=&BorForm%5Bop_param2%5D=&BorForm%5Bop_param3%5D=&undefined='
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
            'Postman-Token': 'cd46031b-12dd-4492-98ea-197c263adf6d'
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        result = response.json()
        if len(result) == 1:
            return Response({'status': 1})
        else:
            try:
                user = models.LibUser.objects.get(libId=request.query_params.get('libId', ''))
                if user.libPsw == request.query_params.get('libPsw', ''):
                    return Response({'status': 0, 'user': user})
                else:
                    return Response({'status': 1})
            except:
                result_json = {}
                for i in result:
                    result_json[i['name']] = i['value']
                lu = models.LibUser(libId=request.query_params.get('libId', ''),
                                    libPsw=request.query_params.get('libPsw', ''),
                                    name=result_json['reader-name'],
                                    department=result_json['reader-department'],
                                    readerType=result_json['reader-type'],
                                    registrationDate=datetime.strptime(result_json['z305_registration_date'], '%Y%m%d'),
                                    expiryDate=datetime.strptime(result_json['z305_expiry_date'], '%Y%m%d'))
                lu.save()
                return Response({'status': 0, 'user': lu})

    @action(methods=['get'], detail=False)
    def borrow_info(self, request):
        search = []
        for i in range(20):
            search.append({
                "name": "明朝那些事",
                "author": "当年明月",
                "position": "信息馆借阅区二楼东",
                "fromTime": "2019-03-26",
                "toTime": "2019-05-26"
            })
        if len(search) > 10:
            search = search[:10]
        return Response(search)

    @action(methods=['get'], detail=False)
    def search_lib(self, request):
        search = []
        for i in range(20):
            search.append({
                "name": "明朝那些事",
                "author": "当年明月",
                "publish": "北京北京联合出版公司 2017"
            })
        if len(search) > 10:
            search = search[:10]
        return Response(search)

    @action(methods=['get'], detail=False)
    def book_detail(self, request):
        bookDetail = {
            "name": "明朝那些事",
            "author": "当年明月",
            "publish": "北京北京联合出版公司 2017",
            "theme": "中国历史 - 明代 - 通俗读物",
            "books": [
                {
                    "status": "阅览",
                    "returnDate": "在架上",
                    "position": "历史学院外借书库",
                    "number": "K248.09/D1764",
                    "code": "401100057610",
                    "rfid": "",
                    "reserve": False
                },
                {
                    "status": "外借书",
                    "returnDate": "2019-6-23",
                    "position": "历史学院外借书库",
                    "number": "K248.09/D1764",
                    "code": "401100057610",
                    "rfid": "",
                    "reserve": False
                },
                {
                    "status": "外借书",
                    "returnDate": "在架上",
                    "position": "历史学院外借书库",
                    "number": "K248.09/D1764",
                    "code": "401100057610",
                    "rfid": "",
                    "reserve": True
                }
            ]
        }
        return Response(bookDetail)

    @action(methods=['get'], detail=False)
    def rank(self, request):
        search = []
        for i in range(20):
            search.append({
                "name": "明朝那些事",
                "author": "当年明月",
                "rank": i + 1,
                "rate": 9.0,
                "borrowTimes": 900
            })
        if len(search) > 10:
            search = search[:10]
        return Response(search)

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (SessionFilter,)

    @action(methods=['get'], detail=False)
    def vertify_session(self, request):
        try:
            user = models.User.objects.get(session=request.query_params.get('session', ''))
            if user.libAccount is None:
                return Response({'login': True, 'libBind': False})
            else:
                return Response({'login': True, 'libBind': True})
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
        if result['errorcode'] == 0:
            user = models.User.objects.get(session=request.query_params.get('session', ''))
            user.wxSessionKey = result['session_key']
            user.save()
            return Response({'status': 0})
        else:
            return Response({'status': 1})

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
            return Response({'status': 0})
        except:
            return Response({'status': 1})


schema_view = get_swagger_view(title='Lib Mini Program API', url=None)
