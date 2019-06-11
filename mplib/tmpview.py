from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response


def test(request):
    return HttpResponse('Test Connection.')


def search_lib(request):
    search = []
    for i in range(20):
        search.append({
            "name": "明朝那些事",
            "author": "当年明月",
            "publish": "北京北京联合出版公司 2017"
            })
    if len(search) > 10:
        search = search[:10]
    return HttpResponse(search)


def detail(request):
    detail = {
    "name":"明朝那些事",
    "author":"当年明月",
    "publish":"北京北京联合出版公司 2017",
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
    return HttpResponse(detail)


def rank(request):
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
    return HttpResponse(search)


def notice(request):
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
    return HttpResponse(search)

